# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('res.partner'))
    company_country_id = fields.Many2one(related='company_id.country_id')
    employee_id = fields.Many2one('hr.employee', string="Employé")
    

    @api.constrains('email')
    def _check_unique_email(self):
        for record in self:
            new_value = record.email
            if new_value:
                existing_records = record.env['res.partner'].search([('email', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("Email existe déja !")

    @api.constrains('mobile')
    def _check_unique_mobile(self):
        for record in self:
            new_value = record.mobile
            if new_value:
                existing_records = record.env['res.partner'].search([('mobile', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("N° mobile existe déja !")