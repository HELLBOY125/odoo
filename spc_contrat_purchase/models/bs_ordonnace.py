# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, modules,fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError


class AccountOrdonnance(models.Model):
    _name="account.ordonnance"
    _description ="bulletin  de soins"
    _order = "id desc"

    sequence = fields.Integer(string="Séquence",default=1)
    user_id = fields.Many2one(
        'res.users', string='Utlisateur',
        default=lambda self: self.env.user, check_company=True)
    request_date = fields.Date(string='Date de création',default=fields.Date.today())
    name =  fields.Char(string="N° Ord",required="1")
    ordonnace_date = fields.Date(string="Date")
    adherant_id = fields.Many2one('hr.employee',string="Adhérent")
    adherent_id = fields.Many2one('res.partner',string="Adhérent")
    adherant_child_id = fields.Many2one('res.partner', string="Béneficaire")
    #malade = fields.Char(string='Malade') 
    médecin = fields.Many2one('res.partner',domain="[('is_medecin','=',True)]",string='Médecin')
    num_bs = fields.Integer(string="N° B.S")
    move_id = fields.Many2one('account.move', string="Facture")
    ref_invoice= fields.Char(string="Réference Facture")
    type_process = fields.Selection([('bs','BS'),
                                     ('prise_charge','Prise en charge')],string="Type de process",default='bs')
    bs_ids = fields.One2many('account.move.line','bs_id',string='lignes de facture',context={'active_test': False}) 
    type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="in_invoice", change_default=True)
   
    company_id = fields.Many2one(comodel_name='res.company', string='Société',readonly=True,default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
        related='company_id.currency_id')
    currency_id = fields.Many2one('res.currency',readonly="1" ,string='Devise',default=lambda self: self.env.ref('base.TND').id)
    attachment_ids = fields.Many2many('ir.attachment','attachment_ordonnace_rel','attachment_id','ordonnace_id', string='Piéces jointes') 
    convention_id = fields.Many2one('purchase.agreement',string="Contrat de convention",compute='_get_convention_adherant')
    state = fields.Selection([('draft','Brouillon'),
                              ('saisie','Entrée saisie'),
                              ('open','Contrôle médecin'),
                              ('done',"Valider"),
                              ('cancel',"Annuler")
                              ],string="État",default='draft')
    line_ids = fields.One2many('account.ordonnance.line', 'ordonnance_id', string='lignes de BS', states={'done': [('readonly', True)]}, copy=False)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
        compute='_compute_amount',digits='Product Price')
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
        compute='_compute_amount',digits='Product Price')
    residu_amount = fields.Monetary(string='Reste', store=True, readonly=True,
        compute='_compute_amount',
        inverse='_inverse_residu_amount',digits='Product Price')
    disc = fields.Float(string="Remise")
    disc_amount = fields.Float(string="T.modérateur",store=True, readonly=True,
        compute='_compute_amount',digits='Product Price')
    amount_total = fields.Float(string="Total TTC",store=True, readonly=True,
        compute='_compute_amount',inverse='_inverse_amount_total',digits='Product Price')    
    charge_adherant = fields.Integer(string="Charge Adhérent(%)",compute="_get_charge")
    charge_company = fields.Integer(string="Charge société (%)",compute="_get_charge")
    dossier = fields.Char(string='Dossier')
    num_chambre = fields.Char(string="N° chambre")
    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")



    @api.onchange('adherent_id')
    def _onchange_adherant_id(self):
        domain=[]
        if self.adherent_id:
            current_employee = self.adherent_id
            domain = ['|',('parent_id', '=', current_employee.id),('name','=',current_employee.name)]
        return {'domain': {'adherant_child_id': domain}}

    
    def _get_charge(self):
        for move in self:
            charge_adherant=0
            charge_company=0
            if move.convention_id:
                charge_adherant= move.convention_id.taux
            else:
                charge_adherant= 100
            charge_company= 100-charge_adherant
            move.charge_adherant= charge_adherant
            move.charge_company= charge_company
            
            
    def confirm_bs(self):
        for move in self:
            if not move.attachment_ids:
                raise UserError(("Il faut ajouter les piéces jointes justificatifs avant de valider !!"))
        move.state='saisie'
    
    
    
    def name_get(self):
        result = []
        for bs in self:
            if not bs.move_id:
                name = '['+bs.name+']' + ' ' + bs.adherent_id.name if  bs.adherent_id else ''
            else:
                name = '['+bs.name+']' + ' ' + bs.adherent_id.name if  bs.adherent_id else '' +'/* %s'%(bs.move_id.name if bs.move_id.name != '/' else bs.move_id.id)
            result.append((bs.id, name))
        return result
    
    @api.depends('line_ids.price_subtotal','line_ids.price_total','line_ids.price_unit','line_ids.quantity')
    def _compute_amount(self):
        amount_untaxed=0.0
        amount_total=0.0
        amount_tax=0.0
        residu_amount=0.0
        disc_amount=0.0
        for move in self:
            for line in move.line_ids:
                amount_untaxed+= line.price_subtotal
                amount_total +=line.price_total 
                residu_amount += line.price_unit* line.quantity
            disc_amount = (amount_total*self.convention_id.taux)/100
            move.amount_untaxed= amount_untaxed 
            move.amount_tax=amount_tax  
            move.disc_amount = disc_amount
            move.residu_amount = amount_total -disc_amount
            move.amount_total=amount_total
            
             


    def _get_convention_adherant(self):
        convention_id=False
        for line in self:
            if line.adherent_id:
                agreement=self.env['purchase.agreement'].sudo().search([('vendor_id','=',line.adherent_id.id),('state','=','done')],limit=1)
                if agreement:
                    convention_id=agreement.id
            line.convention_id=convention_id
            
    # def unlink(self):
    #     for rec in self:
    #         if rec.state != 'draft':
    #             if rec.type_process=='bs':
    #                 raise UserError(_("Vous ne pouvez pas supprimer que une BS à l'état brouillon"))
    #             else:
    #                 raise UserError(_("Vous ne pouvez pas supprimer que une prise en charge à l'état brouillon"))
    #     return super(AccountOrdonnance, self).unlink()  
              
            
class AccountOrdonnanceLine(models.Model):
    _name="account.ordonnance.line"
    _description ="lignes de bulletin  de soins"
    _order = "id desc"     
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Article', domain=[('purchase_ok', '=', True)], required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unité de messure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float(string='Quantité', digits='Product Unit of Measure',default=1)
    price_unit = fields.Float(string='Prix unitaire', digits='Product Price')
    ordonnance_id = fields.Many2one('account.ordonnance', required=True, string='Bulletin de soin', ondelete='cascade')
    company_id = fields.Many2one('res.company', related='ordonnance_id.company_id', string='Société', store=True, readonly=True, default= lambda self: self.env.company)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    currency_id = fields.Many2one(related='ordonnance_id.currency_id', store=True, string='Devise', readonly=True)
    adherant_id = fields.Many2one('res.partner', related='ordonnance_id.adherent_id', string='Adhérent', readonly=True, store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Sous-total', store=True,digits='Product Price')
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True,digits='Product Price')
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True,digits='Product Price')
    description = fields.Text(string='Désignation')  
    conformity_id = fields.Many2one('account.move.conformity',string="Contrôle médecin")
    note = fields.Text(string='Notes')
    parent_state = fields.Selection(related='ordonnance_id.state',string='État')
    
    def button_open(self):
        ir_model_data = self.env['ir.model.data']
        for line in self:
            if not line.conformity_id:
                move_line_id=self.env['account.move.line'].search([('ordonnace_line_id','=',line.id)],limit=1)
                conformity_id=self.env['account.move.conformity'].sudo().create({'move_line_id':move_line_id.id,
                                                                                 'ordonnance_line_id':line.id,
                                                                                 'quantity':line.quantity})
                line.conformity_id=conformity_id.id
                move_line_id.conformity_id=conformity_id.id
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
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            
            self.description =self.product_id.description_purchase or self.product_id.name
            if self.product_id.lst_price:
                self.price_unit = self.product_id.lst_price
            if self.product_id.uom_po_id:
                self.product_uom_id = self.product_id.uom_po_id.id   
                
    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['quantity'],
                vals['product'],
                vals['employee'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            
    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.ordonnance_id.currency_id,
            'quantity': self.quantity,
            'product': self.product_id,
            'employee': self.ordonnance_id.adherent_id,
        }
        
           
   