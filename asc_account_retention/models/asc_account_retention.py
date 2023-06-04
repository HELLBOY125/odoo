# -*- coding: utf-8 -*-
# Part Of AS CONSULTING

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import UserError

class AccountRetention(models.Model):
    _name = 'account.retention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Retenue à la source"
    
    name = fields.Char("Nom de la retenue", required=True)
    percent = fields.Float("Taux de la retenue", required=True, help="Le taux de la retenue est un pourcentage (25%)")
    amount = fields.Monetary("Montant", required=True, help="Montant d'application de la retenue")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company.currency_id)
    debit_account_id = fields.Many2one('account.account', 'Compte Debit', required=True)
    credit_account_id = fields.Many2one('account.account', 'Compte Credit', required=True)
    description = fields.Text("Description")
    active = fields.Boolean('Active', default=True)
    categories = fields.Selection([('categ1', "Honoraires, commissions, courtages, vacations et loyers"),
                                   ('categ2', "Honoraires personnes morales"),
                                   ('categ3', "Marchés"),
                                   ('categ4', "Revenues des capitaux mobiliers"),
                                   ('categ5', "Revenues des bons de caisse au porteur"),
                                   ('categ6', "Jetons de présence")], string="Catégories de retenue", required=True)
    company_id = fields.Many2one("res.company", string="Société", required=True, index=True, default=lambda self: self.env.company,
        help="Company related to this journal")
    

    @api.constrains('percent')
    def _check_percent_consistency(self):
        if self.percent >= 0 and self.percent <= 1:
            return 
        else:
            raise UserError(_("Le taux de la retenue à la source est un pourcentage, il doit être en 0 et 100 !"))