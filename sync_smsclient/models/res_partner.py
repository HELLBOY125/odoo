from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sms_count = fields.Integer(string="SMS", compute='_compute_sms_count')

    def _compute_sms_count(self):
        SmsHistory = self.env['sms.smsclient.history']
        for partner in self:
            partner.sms_count = SmsHistory.search_count([('partner_id', 'child_of', self.id)])

    def get_sms(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'SMS History',
            'view_mode': 'tree',
            'res_model': 'sms.smsclient.history',
            'domain': [('partner_id', 'child_of', self.id)],
            'context': "{'create': False}"
        }