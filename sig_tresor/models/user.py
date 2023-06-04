# -*- coding:utf-8 -*-

from odoo import models, fields


class res_users(models.Model):
    _inherit = 'res.users'
    # _name = 'res.users'

    is_chief = fields.Boolean('Est un Chef de Service', help="Chef de Service ou non")
