# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrEchelon(models.Model):
    _name = 'hr.convention.echelon'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Échelons'

    name = fields.Char(string="Nom de l'échelon", required=True)
    code = fields.Char(string='Code', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Société', default=lambda self: self.env.company)
    category_id = fields.Many2one(comodel_name="hr.convention.category", string="Catégorie")

    @api.constrains('name')
    def _unique_name(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le nom de l'échelon doit être unique"))

    @api.constrains('code')
    def _unique_code(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le code de l'échelon doit être unique"))


class HrCategoryLine(models.Model):
    _name = 'hr.convention.category.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ligne des catégories'

    echelon_id = fields.Many2one(comodel_name="hr.convention.echelon", string="Échelon")
    amount = fields.Float(string='Montant', required=True)
    category_id = fields.Many2one(comodel_name="hr.convention.category", string="Catégorie")


class HrCategory(models.Model):
    _name = 'hr.convention.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Catégories'

    name = fields.Char(string='Nom de la catégorie', required=True)
    code = fields.Char(string='Code', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Société', default=lambda self: self.env.company)
    convention_id = fields.Many2one(related='company_id.convention_id', string="Convention")
    line_ids = fields.One2many(comodel_name='hr.convention.category.line', inverse_name='category_id',
                                  string="Lignes")
    start_date = fields.Date(string="Date de début")
    type = fields.Selection([('monthly', 'Mensuelle'), ('hourly', 'Horaire')])

    @api.constrains('name')
    def _unique_name(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le nom de la catégorie doit être unique"))

    @api.constrains('code')
    def _unique_code(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le code de la catégorie doit être unique"))


class HrConvention(models.Model):
    _name = 'hr.convention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Conventions'

    name = fields.Char(string='Nom de la convention', required=True)
    code = fields.Char(string='Code', required=True)
    category_ids = fields.One2many(comodel_name='hr.convention.category', inverse_name='convention_id',
                                   string="Catégories")

    @api.constrains('name')
    def _unique_name(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le nom de la convention doit être unique"))

    @api.constrains('code')
    def _unique_code(self):
        for record in self:
            obj = self.search([('code', '=ilike', record.name), ('id', '!=', record.id)])
        if obj:
            raise ValidationError(_("Le code de la convention doit être unique"))
