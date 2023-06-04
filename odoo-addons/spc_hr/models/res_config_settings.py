# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_spc_hr_passports_visas = fields.Boolean(string='Gestion des passeports et des visas')