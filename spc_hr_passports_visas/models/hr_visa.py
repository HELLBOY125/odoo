# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class HrVisa(models.Model):
    _name = 'hr.visa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Visa Management'


    #visa management
    name = fields.Char(string='N° Visa', required=True)
    passport_id = fields.Many2one('hr.passport', string="Passeport", required=True, ondelete="cascade", onupdate="cascade")
    employee_id = fields.Many2one('hr.employee', string="Employé", required=True)
    country_id = fields.Many2one('res.country', string="Pays de délivrance", required=True)
    type_visa_id = fields.Many2one('hr.type.visa', string="Type visa", ondelete="restrict", required=True)
    date_debut = fields.Date(string='Date début', required=True)
    date_fin = fields.Date(string='Date fin', required=True)
    show_state = fields.Boolean(default=False)
    state = fields.Selection([('valide', 'Valide'),
                              ('expired', 'Expiré')
                              ], string='Statut', compute='_compute_visa_validity', store=True)

    _sql_constraints = [('name_unique', 'unique(name)', _('N° Visa existe déja'))]

    @api.depends('date_fin')
    def _compute_visa_validity(self):
        actual_date = date.today()
        for record in self:
            if record.date_fin:
                record.show_state = True
                if record.date_fin < actual_date:
                    record.state = 'expired'
                else:
                    record.state = 'valide'

    @api.constrains('date_debut','date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut > record.date_fin:
                raise ValidationError("La date de fin doit être supérieure à la date de début !")

    @api.constrains('name')
    def _check_num_visa(self):
        for record in self:
            if record.name:
                if len(record.name) > 30:
                    raise ValidationError("Le longeur du numéro de visa ne doit pas être supérieur à 30 !")



class HrTypeVisa(models.Model):
    _name = 'hr.type.visa'

    name = fields.Char(string='Type Visa', required=True)