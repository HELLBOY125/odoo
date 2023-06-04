# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, modules,fields, models, _
from datetime import date, timedelta
import calendar
from odoo.exceptions import UserError,ValidationError


class Processmedecin(models.Model):
    _name="process.medecin"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description ="Feuille de présence mensuelle"
    _order = "id desc"

    def get_default_date_start(self):
        date_now= date.today()
        return '%s-%s-01' %(date_now.year,date_now.month)
   
    def get_default_date_end (self):
        date_now= date.today()
        last_day = date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])
        return last_day
   
   
    user_id = fields.Many2one(
        'res.users', string='Utlisateur',
        default=lambda self: self.env.user, check_company=True)
    request_date = fields.Date(string='Date de création',default=fields.Date.today())
    company_id = fields.Many2one(comodel_name='res.company', string='Société',readonly=True,default=lambda self: self.env.company)
    name =  fields.Char(string="N° Feuille")
    date_start = fields.Date(string="Date Début",default=get_default_date_start)
    date_end = fields.Date(string="Date Fin",default=get_default_date_end)
    medecin_id = fields.Many2one('res.partner',string='Médecin/Vacataire')
    type_medecin_id = fields.Many2one('res.partner.medecin',string='Spécialité',related="medecin_id.type_medecin_id")
    line_ids = fields.One2many('process.medecin.line', 'process_medecin_id', string='lignes de feuille',readonly="1", states={'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([('draft','Brouillon'),
                              ('in_progress','En cours de saisie'),
                              ('done',"validé"),
                              ('cancel',"Annuler")
                              ],string="État",default='draft',tracking=True, copy=False)
    
    attachment_ids = fields.Many2many('ir.attachment','attachment_process_medecin_rel','attachment_id','ordonnace_id', string='Piéces jointes') 
    nbre_malade= fields.Integer(string="Nbre des malades",compute="_get_total_malade")
    nbre_vacation= fields.Integer(string="Nbre des vacations",compute="_get_total_vacation")
    move_id = fields.Many2one('account.move', string="Note d'honoraires")
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Ce numéro de feuille existe déjà !"),
    ]


    @api.constrains('date_start','date_end')
    def chech_date(self):
        if self.date_start and self.date_end:
            if self.date_end< self.date_start:
                raise UserError(("une date de fin ne peut pas être antérieure à la date de début !!"))
    
    def btn_ajouter(self):
        move_id=False
        invoice_lines = []
        tarif=0.0
        for rec in self:
            if len(rec.line_ids)==0:
                raise UserError(("Il faut ajouter les lignes de feuille de présence avant de créer la Note d'honoraires  !!"))
            if rec.nbre_malade==0:
                raise UserError(("Il faut ajouter les détailles de béneficaires  !!"))
            journal = self.env['account.journal'].sudo().search([('company_id', '=', self.env.company.id), ('type', '=', 'purchase')], limit=1)       
            vals={'partner_id':rec.medecin_id.id,
                   'journal_id':journal.id,
                   'ref_account':rec.name,
                    'type':'in_invoice',
                    'feuille_presence_id':rec.id,
                    'is_process_medecin':True
                    }
            move_id=self.env['account.move'].create(vals) 
            new_lines = self.env['account.move.line']
            if move_id :
                fiscal_position = move_id.fiscal_position_id
                if rec.type_medecin_id:
                    vacation_id=self.env['res.vacation.config'].search([('type_medecin_id','=',rec.type_medecin_id.id)],limit=1)
                    if vacation_id:
                        if vacation_id.tarif>0:
                            tarif= vacation_id.tarif
                product_id =self.env.ref('spc_contrat_purchase.vacation_product')
                accounts =product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                invoice_line_values= {
                    'move_id': move_id.id,
                    'date_maturity': move_id.invoice_date_due,
                    'product_id': product_id.id,
                    'price_unit': tarif,
                    'quantity': rec.nbre_vacation,
                    'partner_id': rec.medecin_id.id,
                    'account_id':accounts['expense'].id,
                            } 
                invoice_lines.append((0, 0, invoice_line_values))
                rec.move_id =move_id.id 
                move_id.invoice_line_ids= invoice_lines
                ir_model_data = self.env['ir.model.data']
                form_id = ir_model_data.get_object_reference('account','view_move_form')[1]
                return {
                    'name': _("Note d'honoraires de %s" %(rec.medecin_id.name)),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'res_id':move_id.id,
                    'target': 'new',
                        }
        
    @api.depends('line_ids','line_ids.nbre_malade') 
    def _get_total_malade(self):
        nbre_malade=0
        for rec in self:
            if rec.line_ids:
                for line in rec.line_ids:
                    nbre_malade+=line.nbre_malade 
            rec.nbre_malade=nbre_malade


    def _get_total_vacation(self):
        nbre_vacation=0
        for rec in self:
            if rec.line_ids:
                for line in rec.line_ids:
                    nbre_vacation+=line.nbre_vacation 
            rec.nbre_vacation=nbre_vacation
            
    def btn_confirm(self):
        for rec in self:
            for line in rec.line_ids:
                if not line.sans_malade:
                    if line.nbre_malade==0:
                        raise UserError(("Il faut ajouter les détailles de bénefecaires de chaque journée !!"))

            rec.state='done'
            
    def btn_annuler(self):
        for rec in self:
            rec.state='cancel'



    def btn_open(self):
        for rec in self:
            if not (rec.attachment_ids):
                raise UserError(("Il faut ajouter les piéces jointes justificatifs !!"))

            rec.state='in_progress'
            
            
           

class ProcessmedecinLine(models.Model):
    _name="process.medecin.line"
    _description ="les lignes de feuille de présence mensuelle"
    _order = "date asc"

    
    date = fields.Datetime(string="Journée")
    emargement = fields.Boolean(string="Emargement",default=True)
    process_medecin_id = fields.Many2one('process.medecin', required=True, string='Feuille', ondelete='cascade')
    medecin_id = fields.Many2one('res.partner',string='Médecin spécialiste \ vacataire',related="process_medecin_id.medecin_id")
    type_medecin_id = fields.Many2one('res.partner.medecin',string='Spécialité',related="medecin_id.type_medecin_id")
    company_id = fields.Many2one(comodel_name='res.company', string='Société',readonly=True,default=lambda self: self.env.company)
    details_ids = fields.One2many('process.medecin.details', 'detail_id', string='détailles de feuille')
    nbre_malade= fields.Integer(string="Nombres des malades",compute="_get_total_malade")
    nbre_vacation= fields.Integer(string="Nombres des vacations",compute="_get_total_vacation")
    sans_malade = fields.Boolean(string='Journée sans malades')  
    
   
    
    @api.constrains('process_medecin_id', 'date')
    def _check_dates(self):
        for line in self:
            if  line.process_medecin_id.date_start > line.date.date() or  line.process_medecin_id.date_end < line.date.date() :
                raise ValidationError(_("Il faut saisier une date valide !!"))
            
    @api.depends('details_ids')
    def _get_total_malade(self):
        for rec in self:
            rec.nbre_malade=len(rec.details_ids)
            
    def _get_total_vacation(self):
        nbre_vacation=0
        for rec in self:
            if rec.type_medecin_id:
                vacation_id=self.env['res.vacation.config'].search([('type_medecin_id','=',rec.type_medecin_id.id)],limit=1)
                if vacation_id:
                    if vacation_id.number_vacation_limite>0 and vacation_id.tarif>0:
                        if vacation_id.number_vacation_limite>=rec.nbre_malade:
                           nbre_vacation=1
                        else:
                            nbre_vacation=2
                    elif vacation_id.number_vacation_limite==0 and vacation_id.tarif>0:
                        nbre_vacation=1 
                else:
                    nbre_vacation=0                    
            rec.nbre_vacation=nbre_vacation        

class Processmedecindetails(models.Model):
    _name="process.medecin.details"    
    
    
    sequence = fields.Integer(string="Séquence",default=1)
    adherant_id = fields.Many2one('hr.employee', string="Adhérent")
    adherent_id = fields.Many2one('res.partner', string="Adhérent")
    adherant_child_id = fields.Many2one('res.partner', string="Béneficaire")
    matricule = fields.Char(string="Matricule",related="adherent_id.ref",readonly=True)
    detail_id = fields.Many2one('process.medecin.line', required=True, string='béneficaire', ondelete='cascade')
    
    
    _sql_constraints = [
        ("details_user_uniq", "unique (detail_id,adherant_child_id)", "Ce béneficaire existe déjà !")
    ]


    @api.onchange('adherent_id')
    def _onchange_adherent_id(self):
        domain=[]
        if self.adherent_id:
            current_employee = self.adherent_id
            domain = ['|',('parent_id', '=', current_employee.id),('name','=',current_employee.name)]
        return {'domain': {'adherant_child_id': domain}}
    
    
    
    
   

  