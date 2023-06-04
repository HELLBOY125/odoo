# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class TypeCourrierEntrant(models.Model):
	_name = 'type.courrier.entrant'

	name = fields.Char(string="Type", required=True)
	code_id = fields.Char(string="Code", required=True)
	is_pharmacie = fields.Boolean(string='Pharmacie')

	_sql_constraints = [('code_id_unique', 'unique(code_id)', _('Code existe déja !'))]

class TypeCourrierSortant(models.Model):
	_name = 'type.courrier.sortant'
	
	name = fields.Char(string="Type", required=True)
	code_sortant = fields.Char(string="Code", required=True)

	_sql_constraints = [('code_sortant_unique', 'unique(code_sortant)', _('Code existe déja !'))]







