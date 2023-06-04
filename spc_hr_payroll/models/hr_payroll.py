# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta, timezone, date
import datetime
from odoo.exceptions import ValidationError, UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    net_wage_to_pay = fields.Float(compute='_compute_basic_net', string='Salaire net à payer')
    number_of_days_per_month = fields.Float(string='Nb des jours par mois', default=21)
    number_of_hour_per_month = fields.Float(string='Nb des heures par mois', default=168)
    bank_id = fields.Char(string="Numéro de compte")

    def _compute_basic_net(self):
        for payslip in self:
            # payslip.basic_wage = payslip._get_salary_line_total('BASIC')
            # payslip.net_wage = payslip._get_salary_line_total('NET')
            # payslip.net_wage_to_pay = payslip._get_salary_line_total('NET_A_PAY')

            for rec in payslip.employee_id.bank_account_ids:
                if rec.active_account:
                    acc_number = rec.acc_number
                    payslip.bank_id = acc_number

    # @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    # def _onchange_employee(self):
    #     super(HrPayslip, self)._onchange_employee()
    #     self.struct_id = self.contract_id.structure_id.id

    def action_payslip_done(self):
        
        if self.search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done'),
                        ('date_from', '<=', self.date_from), ('date_to', '>=', self.date_to)]):
            raise ValidationError(u"Une seule fiche de paie à l'état Fait par employé pour la même période !")
        else:
            return super(HrPayslip, self).action_payslip_done()

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        contract_obj = self.env['hr.contract']
        rule_obj = self.env['hr.salary.rule']

        struct_obj = self.env['hr.payroll.structure']
        input_obj = self.env['hr.payslip.input']
        prime_obj = self.env['hr.premium']

        primes_ids = contract_obj.browse(contracts.id).hr_premium_line_ids
        # structure_ids = contract_obj.get_all_structures(contracts)
        # rule_ids = struct_obj.get_all_rules(structure_ids)

        contract = contract_obj.browse(contracts.id).id
        # sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]

        for prime_ligne in primes_ids:
            premium_id = prime_ligne['premium_id'].id
            amount = prime_ligne['amount']
            code = prime_obj.browse(premium_id).code
            name = prime_obj.browse(premium_id).name
            payslip_id = self.browse(contracts.id).id
            inputs_line_vals = {
                'code': code,
                'amount': amount,
                'name': name,
                'contract_id': contract,
                'payslip_id': payslip_id,
            }
            exist = input_obj.search([('code', '=', code), ('amount', '=', amount), ('name', '=', name),
                                      ('contract_id', '=', contracts.id), ('payslip_id', '=', payslip_id)],)
            if not exist:
                res += [inputs_line_vals]
        return res

