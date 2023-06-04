# -*- coding:utf-8 -*-

from odoo import models, fields


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    work_matricule = fields.Char('Matricule')
