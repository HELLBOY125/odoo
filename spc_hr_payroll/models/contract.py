# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta, timezone, date
import datetime
from odoo.exceptions import ValidationError, UserError


class HrPremiumContractLine(models.Model):
    _name = 'hr.contrcat.premium.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Liste des Primes des contrats'

    premium_line_id = fields.Many2one(comodel_name='hr.premium.line', string="Paramètage de prime", required=True)
    premium_id = fields.Many2one(related="premium_line_id.premium_id")
    percentage = fields.Float(related="premium_line_id.percentage")
    amount = fields.Float(string="Montant", compute="compute_premium_amount")
    cotisable = fields.Boolean(related="premium_line_id.cotisable")
    imposable = fields.Boolean(related="premium_line_id.imposable")
    absence = fields.Boolean(related="premium_line_id.absence")
    code = fields.Char(related="premium_line_id.code")
    contract_id = fields.Many2one(comodel_name='hr.contract', string="Contrat")

    @api.depends('contract_id', 'contract_id.hr_premium_line_ids')
    def compute_premium_amount(self):
        """"""
        amount = 0.0
        for rec in self:
            if rec.contract_id:
                for line in rec.contract_id.hr_premium_line_ids:
                    if line.premium_line_id:
                        amount = (line.percentage * line.contract_id.wage) / 100
            rec.amount = amount

    @api.onchange('contract_id', 'contract_id.hr_premium_line_ids')
    def onchange_premium_amount(self):
        """"""
        amount = 0.0
        for rec in self:
            if rec.contract_id and rec.contract_id.hr_premium_line_ids:
                for line in rec.contract_id.hr_premium_line_ids:
                    if line.premium_line_id:
                        amount = (line.percentage * line.contract_id.wage) / 100
            rec.amount = amount


class HrContract(models.Model):
    _inherit = 'hr.contract'

    category_id = fields.Many2one(comodel_name='hr.convention.category', string='Catégorie')
    echelon_id = fields.Many2one(comodel_name='hr.convention.echelon', string='Échelon')
    percent = fields.Float(string="Pourcentage d'augmentation")
    convention_wage = fields.Monetary('Salaire par convention', digits=(16, 2), default=0, required=True, tracking=True)
    hr_premium_line_ids = fields.One2many(comodel_name='hr.contrcat.premium.line', inverse_name='contract_id',
                                          string='Primes',  check_company=True)

    @api.onchange('echelon_id', 'category_id')
    def get_convention_wage(self):
        """"""
        for rec in self.env['hr.convention.category'].search([('id', '=', self.category_id.id)]):
            self.convention_wage = rec.line_ids.search([('echelon_id', '=', self.echelon_id.id)], limit=1).amount

    @api.onchange('percent')
    def calculate_wage(self):
        self.wage = self.convention_wage + self.convention_wage * (self.percent / 100)

    name = fields.Char(string='Réference du contrat', required=False)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employé', tracking=True, required=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    wage_per_hour = fields.Monetary(string='Prix par heure')
    premium_caisse = fields.Monetary(string="Prime de caisse")
    premium_panier = fields.Monetary(string="Prime de panier")
    premium_transport = fields.Monetary(string="Indemnité de transport")
    premium_presence = fields.Monetary(string="Indemnité de présence")
    complement_premium = fields.Monetary(string="Prime complémentaire")

    # recup
    gross_wage_conv = fields.Monetary(string='Salaire Brut conventionnelle')
    gross_wage = fields.Monetary(string='Salaire Brut')
    net_wage = fields.Monetary(string='Salaire Net')

    # @api.model
    # def create(self, vals):
    #     name = vals.get('name', False)
    #     employee_id = vals.get('employee_id')
    #     classification_id = vals.get('classification')
    #     if classification_id:
    #         amount = self.env['hr.salary.grid'].browse(classification_id).amount
    #         self.write({'wage': amount})
    #     self.env.cr.execute('SELECT id FROM hr_contract where employee_id=%s AND active =%s', (employee_id, 't'))
    #     self.deadline = self.env.cr.fetchone()
    #
    #     if not self.deadline:
    #         company_id = vals.get('company_id', False)
    #         civp_sequence_code = 'hr.contract.civp.ref'
    #         cdi_sequence_code = 'hr.contract.cdi.ref'
    #         cdd_sequence_code = 'hr.contract.cdd.ref'
    #         type_contract_id = vals.get('type_id', False)
    #         type_contract = self.env['hr.contract.type'].browse(type_contract_id).name
    #         year = datetime.datetime.now().year
    #         if type_contract == 'CIVP':
    #             vals['name'] = type_contract + '/' + str(year) + '/' + str(
    #                 self.env['ir.sequence'].next_by_code(civp_sequence_code))
    #             contract_sivp_id = super(HrContract, self).create(vals)
    #             return contract_sivp_id
    #
    #         if type_contract == "CDI":
    #             vals['name'] = type_contract + '/' + str(year) + '/' + str(
    #                 self.env['ir.sequence'].next_by_code(cdi_sequence_code))
    #             contract_cdi_id = super(HrContract, self).create(vals)
    #             return contract_cdi_id
    #
    #         if type_contract == "CDD":
    #             vals['name'] = type_contract + '/' + str(year) + '/' + str(
    #                 self.env['ir.sequence'].next_by_code(cdd_sequence_code))
    #             contract_cdi_id = super(HrContract, self).create(vals)
    #             return contract_cdi_id
    #     else:
    #         raise ValidationError(u'Un seule contract active par employé !')
    #
