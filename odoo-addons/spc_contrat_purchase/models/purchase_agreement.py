# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, modules,fields, models, _
from datetime import datetime, date, timedelta
import dateutil.relativedelta as relativedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _, html_translate

args_field=['agreement_desc',
            'agreement_titre',
            'vendor_id',
            'date_start_convention',
            'date_end_convention',
            'trial_period',
            'montant_plafond',
            'taux']

CONSULTATION_STATES = [
    ('draft', 'Brouillon'),
    ('confirm','Confirmer'),
    ('done', 'Signé'),
    ('end','Réasiliation'),
    ('cancel', 'Annuler')
]

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),]

class AgreementResiliation(models.Model):
    _name = 'agreement.resiliation'
    _description = 'Motif de résiliation'

    name= fields.Char(string="Motif de résiliation")

class CategoriePurchaseAgreement(models.Model):
    _name = "categorie.purchase.agreement"
    _description = "Type de conventionné"

    type_conventionne = fields.Selection([('physique', 'Physique'),
                                          ('liberale', 'Libérale'),
                                          ('morale','Morale')], string='Conventionné')

    name= fields.Char(string="Nom")


class PurchaseAgreement(models.Model):
    _name = "purchase.agreement"
    _description = "Contrat de convention"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    def _get_categorie_conventione(self):
        return self.env['categorie.purchase.agreement'].sudo().search([('type_conventionne','=',self.env.context.get('default_type_conventionne'))],limit=1)

    
    request_date = fields.Date(string='Date de création',default=fields.Date.today())
    name = fields.Char(string='Convention N°', required=True, copy=False, default='Nouveau', readonly=True)
    user_id = fields.Many2one(
        'res.users', string='Utlisateur',
        default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', string='Société', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Devise',default=lambda self: self.env.ref('base.TND').id)
    type_conventionne = fields.Selection([('physique', 'Physique'),
                                          ('liberale', 'Libérale'),
                                          ('morale','Morale')], string='Conventionné', default='physique')
    categorie_conventione_id = fields.Many2one('categorie.purchase.agreement', string="type de conventionné",default=_get_categorie_conventione)
    vendor_id = fields.Many2one('res.partner', string="D’une part")
    #hr_employee_id = fields.Many2one('hr.employee', string="Adhérent")
    #matricule = fields.Char(string="Matricule",related="hr_employee_id.matricule",readonly=True)
    partner_id = fields.Many2one('res.partner', string="D’autre part",default=lambda self: self.env.company.partner_id)
    matricule = fields.Char(string="Matricule",related="vendor_id.ref",readonly=True)
    contact_id = fields.Many2one('res.partner', string="Contact primaire")
    second_contact_id = fields.Many2one('res.partner', string="Contact secondaire")
    pdg = fields.Many2one('hr.employee',string='Responsable',default=lambda self: self.env.company.responsible_id)
    agreement_titre = fields.Char(string='Titre du convention',default='Contrat de Convention')
    agreement_desc = fields.Text(string='Description du convention')
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
    state = fields.Selection(CONSULTATION_STATES,
                             'Status', tracking=True, required=True,
                             copy=False, default='draft')
    description = fields.Text()
    date_end = fields.Date(string='Date limite de signature')
    article_ids = fields.One2many('purchase.agreement.article.line', 'agreement_id', string='Articles de convention', states={'confirm': [('readonly', True)]}, copy=True)
    montant_plafond = fields.Float(string="Plafond de montant")
    taux = fields.Float(string="Taux(%)")
    prix_unitaire = fields.Float(string="Prix unitaire")
    date_start_convention= fields.Date(string="Date de début",tracking=True)
    date_end_convention= fields.Date(string="Date de fin",tracking=True)
    trial_period = fields.Char(string="Période",compute="_compute_duration")
    attachment_ids = fields.Many2many('ir.attachment','attachment_convention_rel','attachment_id','convention_id', string='Piéces jointes')
    signature_ids = fields.One2many('signature.agreement', 'agreement_id', string='Signature du convention')
    date_resiliation = fields.Date(string="Date de résiliation",readonly="1")
    reason_resiliation = fields.Many2one('agreement.resiliation',string="Motif de résiliation",readonly="1")
    origin = fields.Char(string="Document source")

    def check_deadline_date(self):
        values = []
        activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'À faire')])
        for rec in self.search([]):
            days_to_subtract = 1
            if rec.date_end:
                notification_day = rec.date_end - timedelta(days=days_to_subtract)
                if notification_day == datetime.today().date():
    
                    values.append({"activity_type_id": activity_type_id.id,
                              "date_deadline": rec.date_end,
                              "user_id": rec.pdg.user_id.id,
                              'summary': "Prochaine Expiration du contrat %s" % rec.name,
                              'note': "Le contrat %s va expiré le %s " % (rec.name, rec.date_end),
                              "res_model_id": self.env['ir.model'].search([('model', '=', 'purchase.agreement')]).id,
                              "res_id": rec.id,
                              })
                    rec.message_post(type="notification",
                                     subject="Expiration du contrat %s" % rec.name,
                                     body="Le contrat %s va expiré le %s " % (rec.name, rec.date_end))
                    self.env['mail.activity'].create(values)

    def open_convetion_pdf(self):
        return {
            'type' : 'ir.actions.act_url',
            'url' : '/report/pdf/spc_contrat_purchase.purchase_agreement_report/%s'%self.id,
            'target' : 'new',
        }

    def print_convention(self):
        return self.env.ref('spc_contrat_purchase.report_purchase_agreement').report_action(self)

    def print_resiliation(self):
        return self.env.ref('spc_contrat_purchase.report_purchase_agreement_resiliation').report_action(self)

    @api.constrains('date_start_convention','date_end_convention')
    def check_date(self):
        for rec in self:
            if rec.date_end_convention:
                if rec.date_end_convention < rec.date_start_convention:
                    raise UserError("Il faut que la date du fin  suppérieur à la date début du convention !!")


    @api.onchange('vendor_id')
    def onchange_vendor_id(self):
        if self.vendor_id:
            self.currency_id=self.vendor_id.property_purchase_currency_id.id

    @api.depends('date_start_convention','date_end_convention')
    def _compute_duration(self):
        years=0
        months=0
        days=0
        trial_period=''
        for rec in self:
            if rec.date_start_convention and rec.date_end_convention:
                d1 = rec.date_start_convention
                d2 = rec.date_end_convention
                years = relativedelta.relativedelta(d2, d1).years
                months = relativedelta.relativedelta(d2, d1).months
                days = relativedelta.relativedelta(d2, d1).days
                if years >0 and months >0 and days>0:
                    trial_period = str(years)+' ans et'+' '+str(months)+' mois et'+ ' '+str(days)+' jours'
                elif months >0 and days>0 and years==0:
                    trial_period = str(months)+' mois et'+ ' '+str(days)+' jours'
                elif months >0 and days ==0 and years==0:
                    trial_period = str(months)+' mois'
                elif days>0 and months==0 and years==0:
                    trial_period = str(days)+' jours'
                elif years>0 and months==0 and days==0:
                    trial_period = str(years)+' ans'
                else:
                    trial_period=''
            rec.trial_period =trial_period

    def set_field(self,field):
        if field == 'montant_plafond':
            return '%s' %self.montant_plafond
        elif field == 'taux':
            return '%s' %self.taux
        elif field == 'agreement_desc':
            return self.agreement_desc
        elif field == 'agreement_titre':
            return self.agreement_titre
        elif field == 'vendor_id':
            return self.vendor_id.name
        elif field == 'date_start_convention':
            return '%s' % fields.Date.from_string(self.date_start_convention)
        elif field == 'date_end_convention':
            return '%s' %fields.Date.from_string(self.date_end_convention)

        elif field == 'trial_period':
            return self.trial_period

    def done_agreement(self):
        self.ensure_one()
        self.state='done'


    def cancel_agreement(self):
        self.ensure_one()
        self.state='cancel'

    def validate_agreement(self):
        self.ensure_one()
        if len(self.article_ids)==0:
            raise UserError("Il faut ajouter les articles de convention d'achat avant le confirmer !!")
        #self.name=self.num_agreement 
        if self.name == 'Nouveau':
            if self.type_conventionne=='physique':
                self.name = self.env['ir.sequence'].next_by_code('purchase.agreement.adherant')
            elif self.type_conventionne=='morale':
                self.name = self.env['ir.sequence'].next_by_code('purchase.agreement.morale')
            else:
                self.name = self.env['ir.sequence'].next_by_code('purchase.agreement.liberale')
        self.state='confirm'

    def unlink(self):
        for agreement in self:
            if agreement.state != 'draft':
                raise UserError(_("Vous ne pouvez pas supprimer que la convention à l'état brouillon"))
        return super(PurchaseAgreement, self).unlink()


class PurchaseAgreementArticle(models.Model):
    _name="purchase.agreement.article"
    _order ="sequence"

    sequence = fields.Integer(string="Article N°",index=True)
    name = fields.Char(string='Name',required=True)
    type = fields.Selection([('article','Article'),('autre','Autre')],string='Type',default="article",required=True)
    description = fields.Html(translate=html_translate, sanitize_attributes=False,required=True)
    var_article = fields.Text(string='help',default="$agreement_titre :Titre de convention \n"
                                                    "$agreement_desc :Description de la convention \n"
                                                    "$vendor_id :Contractant \n"
                                                    "$date_start_convention :Date début de convention \n"
                                                    "$date_end_convention :date Fin de convention \n"
                                                    "$trial_periode :Péride de convention \n"
                                                    "$taux :Taux \n"
                                                    "$montant_plafond :Plafond de montant \n")


class PurchaseAgreementArticleLine(models.Model):
    _name="purchase.agreement.article.line"

    sequence = fields.Integer(string="Article N°",index=True, help="Gives the sequence order when displaying a list of articles lines.", default=1)
    article_id = fields.Many2one("purchase.agreement.article",string="Article")
    description = fields.Html(translate=html_translate, sanitize_attributes=False)
    agreement_id = fields.Many2one('purchase.agreement', string='Purchase Agreement', ondelete='cascade')

    @api.onchange('article_id')
    def onchange_article_id(self):
        if self.article_id:
            if self.article_id.description:
                self.description = self.build_expression(self.article_id.description)

    def replace_variable(self,arg,description):
        variable='$%s' %arg
        field =self.agreement_id.set_field(arg)
        result=''
        if arg in args_field:
            if (description.find(variable)!= -1):
                result = field
            else:
                expression=description
        return result


    def build_expression(self, description):
        """Returns a placeholder expression for use in a template field,
        based on the values provided in the placeholder assistant.

        :param $V_arg for arg in ['montnat_plafond','taux']
        :return: final placeholder expression """
        expression = ''
        vals={}
        if description:
            #             if (description.find('$objet_agreement') != -1):
            #                 description=description.replace('$objet_agreement',self.agreement_id.agreement_desc)
            #             else:
            for arg in args_field:
                variable=('$%s' %arg)
                vals.update({variable:self.replace_variable(arg,description)})
            for word, initial in vals.items():
                description = description.replace(word, initial)
        return description

class SignatureAgreement(models.Model):
    _name = "signature.agreement"
    _description = "Signature du convention"

    agreement_id = fields.Many2one('purchase.agreement', string='Convention', ondelete='cascade')
    user_id =fields.Many2one('res.users',string="Membres concernés")
    signature = fields.Selection([('oui','Oui'),('non',"Non")],string="Signature",default='non')
    date_send =  fields.Date(string="Date de l'envoi")
    observation = fields.Text(string="Observation")
    _sql_constraints = [
        ("agreement_user_uniq", "unique (agreement_id,user_id)", "Ce membre existe déjà !")
    ]



    def signed(self):
        self.ensure_one()
        self.signature='oui'

    def no_signed(self):
        self.ensure_one()
        self.signature='non'        