# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'


    matricule_cnss = fields.Char(string="Matricule CNSS")
    matricule_cavis = fields.Char(string="Matricule CAVIS")
    matricule_cnrps = fields.Char(string="Matricule CNRPS")
    fax = fields.Char(string="Fax")
    responsible_id = fields.Many2one("hr.employee", string="Responsable")
