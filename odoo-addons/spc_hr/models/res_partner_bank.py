# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class ResPartnerBank(models.Model):
    _name = 'res.partner.bank'
    _inherit = ['res.partner.bank','mail.thread', 'mail.activity.mixin']

    acc_number = fields.Char('Account Number', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employé", tracking=True)
    bank_id = fields.Many2one('res.bank', string='Bank', ondelete="restrict", tracking=True)
    partner_id = fields.Many2one('res.partner', 'Account Holder', ondelete='cascade', index=True,
                                 domain=['|', ('is_company', '=', True), ('parent_id', '=', False)], required=False,
                                 tracking=True)
    created_date = fields.Date(string="Date d'utilisation", tracking=True)
    active_account = fields.Boolean(string="Actif", tracking=True)
    number_active_account = fields.Integer(string="Nombre de comptes",
                                           compute='_compute_active_count_account_employee_id', store=True,
                                           tracking=True)

    @api.depends('employee_id', 'active_account')
    def _compute_active_count_account_employee_id(self):

        for record in self:
            new_value = False
            current_employee = record.employee_id
            active_accounts=0
            for accounts in current_employee.bank_account_ids:
                count = 0
                new_value = accounts.active_account
                if new_value:
                    count += 1
                accounts.number_active_account = count
                active_accounts = self.env['res.partner.bank'].search_count(
                                      [('employee_id', '=', current_employee.id), ('number_active_account', '=', 1)])
            # if active_accounts > 1:
            #     raise ValidationError("Vous pouvez pas activer plus qu'un compte bancaire !")

    @api.constrains('acc_number')
    def _check_account_number(self):
        for record in self:
            if record.acc_number:
                if not record.acc_number.isalnum():
                    raise ValidationError("Le numéro du compte bancaire ne doit pas contenir des caractères spéciaux !")
                if len(record.acc_number) > 30:
                    raise ValidationError("Le longeur du numéro de compte bancaire ne doit pas être supérieur à 30 !")