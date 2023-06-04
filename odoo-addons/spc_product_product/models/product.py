# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import  UserError ,ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),('product', 'Storable Product')], string='Product Type', default='service', required=True,)
    nature_product = fields.Selection([('fourniture','Fournitures'),
                                       ('medicament','Médicaments'),
                                       ('actes','Actes')],string="Nature",default='fourniture')
    code_pct = fields.Char(string='Code PCT')
    name_commercial = fields.Char(string="Nom commercial")
    price_public = fields.Monetary(string="Prix public",currency_field='currency_id')
    dci = fields.Char(string="DCI")
    code_act = fields.Char(string="Code acte")
    name_act = fields.Char(string="Désignation")
    key = fields.Char(string="Clé")
    
    @api.constrains('code_pct')
    def _check_unique_code_pct(self):
        for record in self:
            new_value = record.code_pct
            if new_value:
                existing_records = record.env['product.template'].search([('code_pct', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("Le code PCT existe déja !")
                
                
    @api.constrains('code_act')
    def _check_unique_code_act(self):
        for record in self:
            new_value = record.code_act
            if new_value:
                existing_records = record.env['product.template'].search([('code_act', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("Le code acte existe déja !")            