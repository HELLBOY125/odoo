# -*- coding: utf-8 -*-

from odoo import models, fields, api

class UrgenceCourrier(models.Model):
	_name = 'courrier.urgence'

	name =fields.Char(string="Urgence", required=True)
	active = fields.Boolean('Active', default=True)
