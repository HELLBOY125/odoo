# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_percent = fields.Float("Pourcentage du prêt")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('ohrms_loan.loan_percent', self.loan_percent)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            loan_percent=float(self.env['ir.config_parameter'].sudo().get_param(
                'ohrms_loan.loan_percent')))

        return res
