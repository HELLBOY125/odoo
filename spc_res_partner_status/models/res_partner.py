# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    status_adherant = fields.Selection([('actif', 'Actif'),
                                        ('retraite', 'Retraité'),], string="État d'adhérent", default='actif')