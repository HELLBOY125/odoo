# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CourrierEntrant(models.Model):
    _name = 'courrier.entrant'
    _inherit = ['mail.thread']
    _description = "Les courriers entrants"
    _order = 'date_courrier desc'

    name = fields.Char(string="Réference", readonly=True)

    reference_courrier_exp = fields.Char("Référence courrier expéditeur")
    type_id = fields.Many2one('type.courrier.entrant', 'Type de courrier', required=True)
    mode_send_id = fields.Many2one('courrier.mode', "Mode de réception")

    state = fields.Selection([
        ('service_courrier', "Service courrier"),
        ('secretariat', "Secretariat"),
        ('directeur', "Directeur"),
        ('sous_direction', "Responsable BO"),
        ('service', "Responsable Service"),
        ('agent', "Agent Service"),
        ('traiter','Traité'),
    ], default='service_courrier', string="État", track_visibility='onchange')

    urgent_id = fields.Many2one(comodel_name='courrier.urgence', string="Mode d'urgence",)
                                #default=lambda self: self.env.ref('spc_bureau_ordre.non_urgent'))
    date_courrier = fields.Date(string='Date de réception', default=fields.Date.today(), required=True)

    street = fields.Char(string="Rue")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="Ville")
    country_id = fields.Many2one('res.country', 'Pays' , ondelete='restrict')
    state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    zip = fields.Char(string="Code postale", size=24, change_default=True)
    website = fields.Char(string="Site Web", help="Website of Partner or Company")

    contact_id = fields.Many2one('res.partner', string="Contact")

    function = fields.Char(string="Poste occupé")
    phone = fields.Char(string="Tél.", default="00 000 000")
    email = fields.Char(string="Courriel")

    is_company = fields.Boolean(help="Check if the contact is a company, otherwise it is a person")
    title = fields.Many2one('res.partner.title', 'Civilité')
    user_id = fields.Many2one('res.users', 'Agent destinataire')

    user_ids = fields.Many2many('res.users', 'courrier_entrant_res_users_rel', 'courrrier_entrant_id', 'user_id',
                                string="Agent destinataire")
    steg_department_id = fields.Many2one('steg.department', string="Département STEG")

    department_id = fields.Many2one('hr.department', string="Département")

    state_color_courrier = fields.Boolean(string="Courrier sans délai de traitement")

    bon_livraison = fields.Selection([('yes', 'Oui'), ('no', 'Non'), ],
                                     string="Avec bon de livraison ?", default="no")
    nb_doc_reçus = fields.Integer(string="Nombre de documents reçus")
    attachement_ids = fields.Many2many('ir.attachment', string="Attachements")

    courrier_traite = fields.Boolean("Courrier Traité",readonly=True)
    date_traitement = fields.Date("Date de traitement", readonly=True)
    is_imput_saved = fields.Integer(default=0)
    courrier_id = fields.Binary('Courrier')

    agent = fields.Many2one("res.users", string="Agent")


    motif = fields.Selection([('1', "Instruction DRSSFD"),
                              ('2', "Instruction CNM"),
                              ('3', "Demande Expresse du SFD")], default='2')

    notes = fields.Html()

    # def act_Prise_en_charge(self):
    #     for record in self:
    #         record.write({'': ''})

    def service_courrier(self):
        self.sudo().state = 'service_courrier'
        if self.sudo().type_id.id == self.env.ref('spc_bureau_ordre.courrier_type_ordre_mission_controle_sur_place').id:
            self.sudo().state = 'agent'

    def retour_service_courrier(self):
        self.sudo().state = 'service_courrier'

    def secretariat(self):
        self.sudo().state = 'secretariat'

    def sous_direction(self):
        self.sudo().state = 'sous_direction'

    def service(self):
        self.sudo().state = 'service'

    def imputer_agent(self):
        self.sudo().state = 'agent'

    def soumettre_directeur(self):
        self.sudo().state = 'directeur'

    def retour_directeur(self):
        self.sudo().state = 'directeur'

    def action_courrier_traite(self):
        """Mettre le champ courrier traité à True pour signaler le traitement de courrier"""
        self.courrier_traite =True
        self.date_traitement = fields.Date.today()
        self.state='traiter'

    def action_courrier_traite_directeur(self):
        """Mettre le champ courrier traité à True pour signaler le traitement de courrier"""
        self.courrier_traite = True
        self.date_traitement = fields.Date.today()

    ####redirection de notification######
    def message_redirect_action(self, cr, uid, context=None):
        if context is None:
            context = {}
        action = self.pool.get('mail.thread').message_redirect_action(cr, uid, context=context)
        return action

    @api.constrains('date_courrier')
    def _check_date_courrier(self):
        current_date = datetime.now().date()
        if self.date_courrier > current_date:
            raise ValidationError(
                _('La date de réception doit être inférieure ou égale à la date ' + str(current_date)))

    @api.model
    def create(self, vals):
        my_date = datetime.now()
        current_year = my_date.year
        type_courrier = self.env['type.courrier.entrant'].search([('id', '=', vals['type_id'])],limit=1)
        code_courrier = type_courrier.code_id
        code_seq = 'CE.' + code_courrier
        ir_sequence_id = self.env['ir.sequence'].search([('code', '=', code_seq)])
        if ir_sequence_id:
            seq_prefix = ir_sequence_id.next_by_code(code_seq)
            vals.update({'name': seq_prefix})
        else:
            val_seq = {"id": "sequence_bureau_ordre_entrant",
                       "name": "CE-" + code_courrier,
                       "code": code_seq,
                       "prefix": "CE/" + str(code_courrier) + "/" + "%(current_year)s" + "/",
                       "use_date_range": True,
                       "padding": 5,
                       "number_increment": 1,
                       }
            ir_sequence_id.sudo().create(val_seq)
            vals['name'] = ir_sequence_id.next_by_code(code_seq)
        result = super(CourrierEntrant, self).create(vals)
        return result

    def write(self, vals):
        if 'type_id' in vals:
            type_courrier = self.env['type.courrier.entrant'].search([('id', '=', vals['type_id'])],limit=1)
            code_courrier = type_courrier.code_id
            code_seq = 'CE.' + code_courrier
            ir_sequence_id = self.env['ir.sequence'].search([('code','=', code_seq)])
            if ir_sequence_id:
                seq_prefix = ir_sequence_id.next_by_code(code_seq)
                vals.update({'name': seq_prefix})
            else:
                val_seq = {"id": "sequence_bureau_ordre_entrant",
                           "name": "CE-" + code_courrier,
                           "code": code_seq,
                           "prefix": "CE/" + str(code_courrier) + "/" + "%(current_year)s" + "/",
                           "use_date_range": True,
                           "padding": 5,
                           "number_increment": 1,
                           }
                self.env['ir.sequence'].sudo().create(val_seq)
                vals.update({'name': self.env['ir.sequence'].next_by_code(code_seq)})
        result = super(CourrierEntrant, self).write(vals)
        return result
