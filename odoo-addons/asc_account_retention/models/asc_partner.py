# -*- coding: utf-8 -*-
# Part Of AS CONSULTING

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    retention_id = fields.Many2one("account.retention", string="Retenue à la source")