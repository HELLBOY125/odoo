# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one(comodel_name='hr.contract.type', string="Type de contrat", required=True,
                              help="Type de contrat",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))