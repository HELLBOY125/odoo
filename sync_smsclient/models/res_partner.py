# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    sms_count = fields.Integer('SMS Count', compute='_compute_sms_count')
    sms_history_ids = fields.One2many('sms.smsclient.history', 'partner_id', 'SMS History')

    @api.depends('sms_history_ids')
    def _compute_sms_count(self):
        for partner in self:
            partner.sms_count = len(partner.sms_history_ids)