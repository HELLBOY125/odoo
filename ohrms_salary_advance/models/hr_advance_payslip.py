# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        adv_salary = self.env['salary.advance'].search([('employee_id', '=', emp_id.id),
                                                        ('state', '=', 'approve'),
                                                        ('paid', '=', False)])
        for adv_obj in adv_salary:
            current_date = date_from.month
            date = adv_obj.date
            existing_date = date.month
            if current_date == existing_date:
                state = adv_obj.state
                amount = adv_obj.advance
                if state == 'approve' and amount != 0 and not adv_obj.paid:
                    input_data = {
                        'name': adv_obj.name,
                        'code': 'SAR',
                        'amount': adv_obj.advance,
                        'contract_id': contract_ids[0].id,
                    }
                    res += [input_data]
        return res

    def action_payslip_done(self):
        advance_obj = self.env['salary.advance'].search([('employee_id', '=', self.employee_id.id),
                                                         ('date', '<=', self.date_to),
                                                         ('state', '=', 'approve'),
                                                         ('date', '>=', self.date_from)])
        if advance_obj:
            for rec in advance_obj:
                if not rec.paid:
                    rec.write({'paid': True})
                    return super(HrPayslip, self).action_payslip_done()
                else:
                    return super(HrPayslip, self).action_payslip_done()
        else:
            return super(HrPayslip, self).action_payslip_done()
