# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class SigTresorDistrict(models.Model):
    _name = 'sig.tresor.district'
    _description = 'District'
    _rec_name = "district_name"

    district_code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_code(), )
    district_name = fields.Char(string='Nom', required=True)
    region_ids = fields.One2many('sig.tresor.region', 'district_id', 'Région')

    _sql_constraints = [
        ('district_name_unique',
         'UNIQUE(district_name)',
         _("Le nom doit être unique !")),
    ]

    @api.model
    def _get_default_code(self):
        """
        ramène le code suivant du district
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.district')
        print('code %s ' % code)
        return code


class SigTresorRegion(models.Model):
    _name = 'sig.tresor.region'
    _description = 'Region'
    _rec_name = "region_name"

    region_code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_region_code(), )
    region_name = fields.Char(string='Nom', required=True)
    country_id = fields.Many2one('res.country', 'Pays',
                                 default=lambda self: self.env['res.country'].search([('code', '=', 'CI')]), )
    district_id = fields.Many2one('sig.tresor.district', 'District', required=True)
    departement_ids = fields.One2many('sig.tresor.departement', 'region_id', 'Départements')

    _sql_constraints = [
        ('region_code_unique',
         'UNIQUE(region_code)',
         _("Le code doit être unique !")),

    ]

    @api.model
    def _get_default_region_code(self):
        """
        ramène le code suivant de la région
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.region')
        print('code %s ' % code)
        return code


class SigTresorDepartement(models.Model):
    _name = 'sig.tresor.departement'
    _description = 'Departement'
    _rec_name = "departement_name"

    departement_code = fields.Char(string='Code', required=True,
                                   default=lambda self: self._get_default_departement_code(), )
    departement_name = fields.Char(string='Nom', required=True)
    region_id = fields.Many2one('sig.tresor.region', 'Région', required=True)
    commune_ids = fields.One2many('sig.tresor.commune', 'departement_id', 'Commune')

    _sql_constraints = [
        ('departement_code_unique',
         'UNIQUE(departement_code)',
         _("Le code doit être unique !")),

    ]

    @api.model
    def _get_default_departement_code(self):
        """
        ramène le code suivant du département
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.departement')
        print('code %s ' % code)
        return code


class SigTresorCommune(models.Model):
    _name = 'sig.tresor.commune'
    _description = 'Commune'
    _rec_name = "commune_name"

    commune_code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_commune_code(), )
    commune_name = fields.Char(string='Nom', required=True)
    departement_id = fields.Many2one('sig.tresor.departement', 'Département', required=True)
    village_ids = fields.One2many('sig.tresor.village', 'commune_id', 'Village')

    _sql_constraints = [
        ('commune_code_unique',
         'UNIQUE(commune_code)',
         _("Le code doit être unique !")),
    ]

    @api.model
    def _get_default_commune_code(self):
        """
        ramène le code suivant de la commune ou sous - préfecture
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.commune')
        print('code %s ' % code)
        return code


class SigTresorvillage(models.Model):
    _name = 'sig.tresor.village'
    _description = 'Village'
    _rec_name = "village_name"

    village_code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_village_code(), )
    village_name = fields.Char(string='Nom', required=True)
    commune_id = fields.Many2one('sig.tresor.commune', 'Commune / Sous - Préfecture', required=True)

    _sql_constraints = [
        ('village_code_unique',
         'UNIQUE(village_code)',
         _("Le code doit être unique !")),
    ]

    @api.model
    def _get_default_village_code(self):
        """
        ramène le code suivant du village
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.village')
        print('code %s ' % code)
        return code
