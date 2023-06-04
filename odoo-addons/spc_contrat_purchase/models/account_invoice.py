# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
    
   
class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    type_partner = fields.Selection([('ordinaire', 'Ordinaire'),
                                     ('conventionne', 'Conventionné'),
                                     ], string='Type', related='partner_id.type_partner')
    ordonnace_ids = fields.One2many('account.ordonnance','move_id',string='Bulletin de soin')
    convention_id = fields.Many2one('purchase.agreement',string="Contrat de convention",compute='_get_convention')
    is_controle = fields.Boolean('Envoi vers controle medecin')
    is_controle_valide = fields.Boolean('Validate controle medecin') 
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    state = fields.Selection(selection_add=[('controle', 'Contrôle médecin'), ('conform', 'Conforme'), ('confirm', 'Valider')], default='draft')
    state_bs = fields.Selection([('draft', 'Brouillon'),
                                 ('controle', 'Contrôle médecin'),
                                 ('confirm', 'Valider'),
                                 ('conform', 'Conforme'),
                                 ('posted', 'Comptabilisé'),
                                 ('cancel', 'Annuler')], compute='_set_state')
    ref_account = fields.Char(string="Réf. facture fournissur")
    invoice_total = fields.Monetary(string="Montant total fournisseur")
    courrier_entrant_id = fields.Many2one('courrier.entrant',string="Courrier entrant")
    is_process_medecin = fields.Boolean(string="Note d'honoraires")
    feuille_presence_id =  fields.Many2one('process.medecin',string="Feuille de présence")
    period = fields.Char(string="Période",compute="_compute_period")
    is_egal = fields.Boolean('totaux conforme',compute="_check_is_egaux")
    is_prise_en_charge = fields.Boolean(string='Prise en charge')
    
    @api.depends('invoice_total','amount_total')
    def _check_is_egaux(self):
        for rec in self:
            if rec.invoice_total==rec.amount_total:
                rec.is_egal=True
            else:
                rec.is_egal=False    
    
    @api.depends('is_process_medecin','feuille_presence_id')
    def _compute_period(self):
        period=''
        for rec in self:
            if rec.is_process_medecin:
                if rec.feuille_presence_id:
                    period ='%s / %s' %(rec.feuille_presence_id.date_start,rec.feuille_presence_id.date_end)
            self.period=period        
    
    @api.depends('state')
    def _set_state(self):
        for requisition in self:
            requisition.state_bs = requisition.state
            
            
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        if self.state != 'posted':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.type]
        if not self.is_process_medecin :   
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name
        else:
            if not self.name or self.name == '/':
                draft_name = "Note d'honoraires (* %s)" % str(self.id)
            else:
                draft_name = "Note d'honoraires  " + self.name 
        return (draft_name or self.name) + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')        
    
    def action_envoie_controle(self):
        for move in self:
            if len(self.ordonnace_ids) ==0:
                raise UserError(('Il faut saisir les bulletin de soin avant le contrôle médecin '))
            if len(self.invoice_line_ids) ==0:
                raise UserError(('Il faut saisir les lignes de facture avant le contrôle médecin '))
            for line in self.ordonnace_ids:
                line.state="open"
                for move_line in line.bs_ids:
                    move_line.is_controle=True
            for move_line in move.line_ids:
                if not move_line.conformity_id:
                    conformity_id=self.env['account.move.conformity'].sudo().create({'move_line_id':move_line.id,'quantity':move_line.quantity,'state':'done',
                                                                                     'type_process':'bs' if move.is_prise_en_charge==False else 'prise_charge'})
                    move_line.conformity_id=conformity_id.id        
            move.is_controle=True 
            move.state="controle"
            
  
                
    def action_done_controle(self):
        for move in self:
            for line in self.ordonnace_ids:
                for move_line in self.invoice_line_ids:
                    move_line.is_controle=True
                    if move_line.conformity_id.status not in ('conforme','no_conforme'):
                        raise UserError(('Il faut saisir le  contrôle médecin de lignes de facture de bulletin de soin N° %s ') %(move_line.bs_id.name))
                    move_line.ordonnace_line_id.conformity_id= move_line.conformity_id.id
                line.state='done'        
            for line in self.line_ids:
                if line.status=='no_conforme':
                    
                    if line.retenue=='pharmacie' or line.ordonnace_line_id.conformity_id.type_process=='prise_charge':
                        line.quantity=0
                if line.status=='conforme':
                    print ('line.ordonnace_line_id.conformity_id.type_process____',line.ordonnace_line_id.conformity_id.type_process)
                    if line.retenue=='pharmacie' or line.ordonnace_line_id.conformity_id.type_process=='prise_charge':
                        query = """ UPDATE account_move_line SET quantity = %s WHERE id= %s"""
                        self.env.cr.execute(query, [line.conformity_id.quantity,line.id])
            move._recompute_dynamic_lines()
            move.with_context(check_move_validity=False)._onchange_currency()   
            move.is_controle_valide=True            
            move.state='confirm'

    def _get_convention(self):
        convention_id=False
        for line in self:
            if line.partner_id:
                agreement=self.env['purchase.agreement'].sudo().search([('vendor_id','=',line.partner_id.id),('state','=','done')],limit=1)
                if agreement:
                    convention_id=agreement.id
            line.convention_id=convention_id


    @api.model
    def _refund_cleanup_lines(self, lines):
        result = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        for i, line in enumerate(lines):
            for name, field in line._fields.items():
                if name == 'bs_id':
                    result[i][2][name] = False
                    break
        return result

    def action_controle_conformity(self):
        for move in self:
            move._recompute_dynamic_lines()
            move.with_context(check_move_validity=False)._onchange_currency()
            move.state = 'conform'


class AccountMoveConformity(models.Model):
    _name = 'account.move.conformity'
    _description = "Contrôle médecin"

    date = fields.Date(string="Date", default=fields.Date.today())
    motif = fields.Many2one('account.move.conformity.reason', string="Motif")
    move_line_id = fields.Many2one('account.move.line', readonly=True)
    quantity  = fields.Float(string='Quantity', digits='Product Unit of Measure')
    ordonnance_line_id = fields.Many2one('account.ordonnance.line', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Piéces jointes")
    user_id = fields.Many2one('res.users', string='Médecin de Contrôle', default=lambda self: self.env.user)
    status = fields.Selection([('conforme', 'Conforme'), ('no_conforme', 'Non conforme')],default='conforme', string="État")
    retenue = fields.Selection([('adherent', 'Adhérent'), ('pharmacie', 'Pharmacie')], string="Retenue")
    state = fields.Selection([('draft', 'Brouillon'),
                              ('done', "Valider"),
                              ], string="État", default='draft')
    
    parent_state = fields.Selection(related='move_line_id.parent_state',string='État')
    type_process = fields.Selection([('bs','BS'),
                                     ('prise_charge','Prise en charge')],string="Type de process",default='bs')
    
    @api.depends('ordonnance_line_id','ordonnance_line_id.ordonnance_id')
    def get_state(self):
        for rec in self:
            parent_state=''
            print ('rec.ordonnance_line_id')
            if rec.ordonnance_line_id:
                if rec.ordonnance_line_id.ordonnance_id:
                    parent_state =  rec.ordonnance_line_id.ordonnance_id.state  
            rec.parent_state=parent_state        

    def validate(self):
        self.state='done'
        ir_model_data = self.env['ir.model.data']
        form_id = ir_model_data.get_object_reference('spc_contrat_purchase', 'view_account_move_confirmity_form')[1]
        return {
                    'name': _('Contrôle médecin'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move.conformity',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'res_id':self.id,
                    'target': 'new',
                }    
        
        
    def button_draft(self): 
        self.state='draft'
        ir_model_data = self.env['ir.model.data']
        form_id = ir_model_data.get_object_reference('spc_contrat_purchase', 'view_account_move_confirmity_form')[1]
        return {
                    'name': _('Contrôle médecin'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move.conformity',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'res_id':self.id,
                    'target': 'new',
                }    


class MotifControlConformity(models.Model):
    _name = 'account.move.conformity.reason'
    _description = "Motif du contrôle médecin"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bs_id = fields.Many2one('account.ordonnance',string="BS")
    conformity_id = fields.Many2one('account.move.conformity',string="Contrôle médecin")
    status = fields.Selection([('conforme','Conforme'),('no_conforme','Non conforme')], string="État",related="conformity_id.status")
    is_controle = fields.Boolean('Envoi vers Contrôle médecin')
    active = fields.Boolean(string='active',default=True)
    ordonnace_line_id =fields.Many2one('account.ordonnance.line',string="ligne de BS") 
    old_quantity = fields.Float(string="Ancien quantité",related="ordonnace_line_id.quantity")
    retenue = fields.Selection( string="Retenue",related="conformity_id.retenue")

   
    def button_open(self):
        ir_model_data = self.env['ir.model.data']
        for line in self:
            line._onchange_price_subtotal() 
            if not line.conformity_id:
                conformity_id=self.env['account.move.conformity'].sudo().create({'move_line_id':line.id,'quantity':line.quantity,'state':'done',
                                                                                     'type_process':'bs' if move_id.is_prise_en_charge==False else 'prise_charge'})
                line.conformity_id=conformity_id.id
            form_id = ir_model_data.get_object_reference('spc_contrat_purchase', 'view_account_move_confirmity_form')[1]
            return {
                    'name': _('Contrôle médecin'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move.conformity',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'res_id':line.conformity_id.id,
                    'target': 'new',
                }    
        
    @api.onchange('product_id','move_id','move_id.convention_id')
    def onchange_bs_id(self):
        domain=[]
        if self.move_id:
            if self.move_id.convention_id:
                self.discount=100-self.move_id.convention_id.taux
                
                
           

    