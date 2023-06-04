# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date




    
class AddInvoiceWizard(models.TransientModel):
    _name = 'add.invoice.wizard'
    _description = 'Ajouter Facture globale'

    partner_id = fields.Many2one('res.partner',string='Fournisseur')
    ref_invoice = fields.Char(string="Réference Facture")
    amount_total = fields.Float(string="Total fournisseur 100%",digits="Product Price")
    total = fields.Float(string="Total saisies",digits="Product Price")
    type_process = fields.Selection([('bs','BS'),
                                     ('prise_charge','Prise en charge')],string="Type de process")
    
    
    is_different = fields.Boolean(string='Différent')
    
    @api.depends('amount_total','total')
    def _is_different(self):
        for rec in self:
            is_different=False
            if rec.total==rec.amount_total:
                is_different=True
            else:
                is_different=False
                
            rec.is_different=is_different        
        



    @api.model
    def default_get(self, fields):
        lst_ref_invoice=[]
        res = super(AddInvoiceWizard, self).default_get(fields)
        bs_ids =  self._context.get('active_ids')
        ordonnance_ids = self.env['account.ordonnance'].browse(bs_ids)
        ref_invoice=''
        total=0
        for bs in ordonnance_ids:
            lst_ref_invoice.append(bs.ref_invoice)
            total+=bs.amount_total
        lst_ref_invoice = list(set(lst_ref_invoice))
        if len(lst_ref_invoice)>1:
            raise UserError(_('Il faut choisir les lignes de méme réference facture !!'))
        res.update({'ref_invoice': lst_ref_invoice[0],'type_process':ordonnance_ids[0].type_process,'total':total})    
        return res
    
    @api.onchange('amount_total','total')
    def onchange_amount(self):
        is_different=False
        if self.total==self.amount_total:
            self.is_different=True
        else:
            self.is_different=False
                
        
  
  
    @api.onchange('type_process')
    def onchange_type_process(self):
        if self.type_process=='prise_charge':
            domain=[('type_partner','=','conventionne'),('type_conventionne','=','morale')]
        else:
            domain=[('type_partner','=','conventionne'),('type_conventionne','=','liberale'),('is_medecin','=',False)]    
        return {'domain': {'partner_id': domain}}
    
  
            
    def validate(self):
        res_ids = self._context.get('active_ids')
        ordonnace_ids = self.env['account.ordonnance'].browse(res_ids)
        print ('ordonnace_ids[0].type_process____',ordonnace_ids[0].type_process)
        lst_ordonnace=[]
        move_id=False
        invoice_lines = []
        for wizard in self:
            for ordonnace in ordonnace_ids:
                #ordonnace.state=='saisie' and
                if  not ordonnace.move_id:
                   lst_ordonnace.append(ordonnace) 
            print ('lst_ordonnace_____',lst_ordonnace)
            if len(lst_ordonnace)>0:
                journal = self.env['account.journal'].sudo().search([('company_id', '=', self.env.company.id), ('type', '=', 'purchase')], limit=1)       
                vals={'partner_id':wizard.partner_id.id,
                      'journal_id':journal.id,
                      'ref_account':wizard.ref_invoice,
                      'type':'in_invoice',
                     'ordonnace_ids':res_ids,
                     'is_prise_en_charge':True if ordonnace_ids[0].type_process=='prise_charge' else False}   
                move_id=self.env['account.move'].create(vals) 
                print ('move_id___________',move_id)
                new_lines = self.env['account.move.line']
                if move_id :
                    print ('11111111111111111111')
                    fiscal_position = move_id.fiscal_position_id
                     
                    for ordonnace in lst_ordonnace:
                        if ordonnace:  
                            if ordonnace.line_ids:  
                                ordonnace.move_id =move_id.id
                                for line in ordonnace.line_ids:
                                    if line.product_id:
                                        accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                                        invoice_line_values= {
                                        'move_id': move_id.id,
                                        'currency_id': line.currency_id.id,
                                        'company_currency_id': line.currency_id.id,
                                        'ordonnace_line_id': line.id,
                                        'bs_id':ordonnace.id,
                                        'date_maturity': move_id.invoice_date_due,
                                        'product_uom_id': line.product_uom_id.id,
                                        'product_id': line.product_id.id,
                                        'price_unit': line.price_unit,
                                        'quantity': line.quantity,
                                        'partner_id': move_id.partner_id.id,
                                        'discount': (100 - move_id.convention_id.taux) if move_id.convention_id else 0,
                                        'account_id':accounts['expense'].id,
                                    } 
                                    invoice_lines.append((0, 0, invoice_line_values))
        
                move_id.invoice_line_ids= invoice_lines
                move_id.action_envoie_controle() 
                move_id.invoice_total=wizard.amount_total
                ir_model_data = self.env['ir.model.data']
                form_id = ir_model_data.get_object_reference('account','view_move_form')[1]
                return {
                    'name': _('Facture globale de %s' %(wizard.partner_id.name)),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'res_id':move_id.id,
                    'target': 'current',
                    'context':{'edit':0}
                        }
            else:
                if ordonnace_ids[0].type_process=='prise_charge':
                    raise UserError(('Tous les prises en charges sont attachées à des factures !!'))
                else:
                    raise UserError(('Tous les BS sont attachées à des factures !!'))                
        
     
    
     