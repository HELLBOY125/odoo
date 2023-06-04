# -*- coding: utf-8 -*-
# Part Of AS CONSULTING

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    account_tax_id = fields.Many2one('account.tax',string="Timbre Fiscal à la vente")
    asc_account_purchase_tax_id = fields.Many2one('account.tax',string="Timbre Fiscal à l'achat")
    applicate_out_timbre = fields.Boolean("Appliquer le timbre fiscal par défaut sur les factures de vente", default=False)
    applicate_in_timbre = fields.Boolean("Appliquer le timbre fiscal par défaut sur les factures d'achat", default=False)