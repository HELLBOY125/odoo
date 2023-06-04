# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import html_translate

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_tax_id = fields.Many2one('account.tax', related="company_id.account_tax_id", string="Timbre Fiscal à la vente", readonly=False)
    asc_account_purchase_tax_id = fields.Many2one('account.tax', related="company_id.asc_account_purchase_tax_id", string="Timbre Fiscal à l'achat", readonly=False)
    applicate_out_timbre = fields.Boolean(string="Appliquer le timbre fiscal par défaut sur les factures/Avoirs de vente", related='company_id.applicate_out_timbre', readonly=False)
    applicate_in_timbre = fields.Boolean(string="Appliquer le timbre fiscal par défaut sur les factures/Avoirs d'achat", related='company_id.applicate_in_timbre', readonly=False)


    def set_values(self):
        super(ResConfigSettings, self).set_values()
 
    
    
   
   

   



