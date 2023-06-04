# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allocation_day_per_cadre = fields.Float(string="Cadre", default=1.9)
    allocation_day_per_employee = fields.Float(string="Employé", default=1.5)