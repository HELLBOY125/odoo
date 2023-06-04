# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re


class ResSpeciality(models.Model):
    _name = 'res.speciality'

    name = fields.Char(string="Spécialité")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type_partner = fields.Selection([('ordinaire', 'Ordinaire'),
                                     ('conventionne', 'Conventionné'),
                                     ], string='Type', default='ordinaire')

    type_conventionne = fields.Selection([('physique', 'Physique'),
                                          ('liberale', 'Libérale'),
                                          ('morale', 'Morale'),
                                          ], string='Conventionné', default='physique')

    cle = fields.Char(string="CLé")
    speciality_id = fields.Many2one('res.speciality', string="Spécialité")
    matricule_fiscale = fields.Char(string='Matricule fiscale', size=13)
    cin = fields.Char(string="Carte d'identité")
    registre_commerce = fields.Char(string='Registre de commerce')
    fax = fields.Char(string='Fax')
    
    _sql_constraints = [('matricule_unique', 'unique(matricule_fiscale)', _('Matricule fiscale existe déja !'))]

    @api.constrains('cin')
    def _check_cin(self):
        for record in self:
            new_value = record.cin
            if new_value:
                if not (re.match(r"^[0-9]+$", new_value)):
                    raise ValidationError("La carte d'identité ne doit pas contenir que des numéros!")

    @api.constrains('cin')
    def _check_unique_cin(self):
        for record in self:
            new_value = record.cin
            if new_value:
                existing_records = record.env['res.partner'].search([('cin', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("La carte d'identité existe déja !")

#     @api.constrains('cin', 'matricule_fiscale')
#     def _check_remplie_cin_matricule(self):
#         for record in self:
#             if (record.cin or record.matricule_fiscale) == False:
#                 raise ValidationError("La carte d'identité ou le matricule fiscale doit etre remplie!")

