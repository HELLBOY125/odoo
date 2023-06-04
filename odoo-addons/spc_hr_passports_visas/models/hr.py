# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = 'hr.employee'

    #Solution 1
    # passports_ids = fields.One2many('hr.passport', inverse_name='employee_id', string="Passeports et visas", ondelete="restrict")
    visa_ids = fields.One2many('hr.visa', inverse_name='employee_id', string="Visas", readonly=False, ondelete="restrict", domain=[('state', '=', 'valide')])
    visas_count = fields.Integer(compute='compute_count_visas')

    def compute_count_visas(self):
        for record in self:
            record.visas_count = self.env['hr.visa'].search_count(
                [('employee_id', '=', record.id)])

    def get_visas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Passeports et visas',
            'view_mode': 'tree,form',
            'res_model': 'hr.visa',
            'domain': [('employee_id', '=', self.id)],
        }

    def open_passport_form(self):
        context = {'default_employee_id': self.id}
        action = {
            'name': 'Créer : Passeport',
            'view_mode': 'form',
            'res_model': 'hr.passport',
            'view_id': self.env.ref('spc_hr_passports_visas.hr_passport_view_form_2').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
        return action