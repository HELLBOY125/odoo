# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, datetime

class HrPassport(models.Model):
    _name = 'hr.passport'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Passport'

    #passport management
    employee_id = fields.Many2one('hr.employee', string="Employé", required=True)
    name = fields.Char(string='N° Passeport', required=True)
    date_delivrance = fields.Date(string="Date de délivrance", required=True)
    date_expiration = fields.Date(string="Date d'expiration", required=True)
    country_id = fields.Many2one('res.country', string="Pays de délivrance", required=True)
    visa_ids = fields.One2many(comodel_name='hr.visa', inverse_name='passport_id', string="Visas", ondelete="restrict")
    show_state = fields.Boolean(default=False)
    attachments_ids = fields.Many2many('ir.attachment', string="Attachements")
    state = fields.Selection([('valide', 'Valide'),
                              ('expired', 'Expiré')
                              ], string='Statut', compute='_compute_passport_validity', store=True)

    _sql_constraints = [('name_unique', 'unique(name)', _('N° Passeport existe déja'))]

    @api.depends('date_expiration')
    def _compute_passport_validity(self):
        actual_date = date.today()
        for record in self:
            if record.date_expiration:
                record.show_state = True
                if record.date_expiration < actual_date:
                    record.state = 'expired'
                else:
                    record.state = 'valide'

    @api.constrains('date_delivrance', 'date_expiration')
    def _check_dates(self):
        if self.date_delivrance > self.date_expiration:
            raise ValidationError("La date d'expiration doit être supérieure à la date de délivrance !")

    @api.constrains('name')
    def _check_passport_numero(self):
        if self.name:
            if not self.name.isalnum():
                raise ValidationError("Le numéro du passeport ne doit pas contenir des caractères spéciaux !")

    @api.depends('name', 'date_delivrance', 'date_expiration')
    def name_get(self):
        res = []
        for record in self:
            date_deliv = record.date_delivrance.strftime('%d/%m/%Y')
            date_exp = record.date_expiration.strftime('%d/%m/%Y')
            name = record.name + ' (' + date_deliv + '-' + date_exp + ')'
            res.append((record.id, name))
        return res

