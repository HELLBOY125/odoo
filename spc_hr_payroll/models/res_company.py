
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from datetime import datetime , timedelta, timezone, date
import datetime


class res_company(models.Model):
    _inherit = 'res.company'

    plafond_security = fields.Float(string='Plafond de la Securite Sociale', digits='Payroll')
    nbr_employee = fields.Integer(string='Nombre d\'employes')
    cotisation_prevoyance = fields.Float(string='Cotisation Patronale Prevoyance',
                                         digits='Payroll')
    org_security_social = fields.Char(string='Organisme de securite sociale', translate=True)
    code_exploitation = fields.Char(string='Code d\'exploitation')
    bureau_regional = fields.Char(string='Bureau regional', translate=True)
    convention_id = fields.Many2one(comodel_name='hr.convention', string='Convention collective')