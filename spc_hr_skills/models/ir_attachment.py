# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    hr_resume_line_id = fields.Many2one(comodel_name='hr.resume.line')
    legalized_document = fields.Boolean(string="Légalisé")
    lang_id = fields.Many2one('res.lang', string="Langue", domain=['|', ('active', '=', True), ('active', '=', False)])
    translated_document = fields.Boolean(string="Traduit")
