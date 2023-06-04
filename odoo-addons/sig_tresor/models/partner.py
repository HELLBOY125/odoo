# -*- coding:utf-8 -*-

from odoo import models, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_armateur = fields.Boolean('Est un armateur', default=False)
