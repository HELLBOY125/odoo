# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date

class ResPartner(models.Model):
    _inherit = "res.partner"

    employee_id = fields.Many2one('hr.employee', string="Employé")
    
