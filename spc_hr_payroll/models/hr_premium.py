# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta, timezone, date
import datetime
from odoo.exceptions import ValidationError, UserError


class HrPremium(models.Model):
    _name = 'hr.premium'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prime'

    name = fields.Char(string="Prime", required=True)
    code = fields.Char(string="Code", required=True)

    @api.constrains('name')
    def _unique_name(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le nom du prime doit être unique"))

    @api.constrains('code')
    def _unique_code(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le code du prime doit être unique"))


class HrPremiumLine(models.Model):
    _name = 'hr.premium.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Liste des Primes'

    name = fields.Char(string='Titre', tracking=True, required=True)
    premium_id = fields.Many2one(comodel_name="hr.premium", string="Prime", required=True, tracking=True)
    percentage = fields.Float(string="Pourcentage", tracking=True)
    cotisable = fields.Boolean(string="Cotisable", tracking=True)
    imposable = fields.Boolean(string="Imposable", tracking=True)
    absence = fields.Boolean(string="Absence", tracking=True)
    code = fields.Char(related="premium_id.code", required=True, tracking=True)

    @api.onchange('cotisable')
    def onchange_cotisable(self):
        if self.cotisable:
            return {'value': {'imposable' : True}}

    def add_premium(self):
        context = {'cotisable': self.cotisable,
                   'imposable': self.imposable,
                   'absence': self.absence,
                   'percentage': self.percentage,
                   'premium_id': self.premium_id.id,
                   'code': self.code}
        action = self.env.ref('spc_hr_payroll.action_hr_premuim_rules_wizard').read()[0]
        action['context'] = context
        return action

