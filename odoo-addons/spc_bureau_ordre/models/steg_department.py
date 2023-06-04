# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StegDepartment(models.Model):
   _name = 'steg.department'
   _description = "Département"
   _inherit = ['mail.thread', 'mail.activity.mixin']

   name = fields.Char("Département", required=True)
