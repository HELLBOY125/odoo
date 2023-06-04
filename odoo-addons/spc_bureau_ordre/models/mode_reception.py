# -*- coding: utf-8 -*-

from openerp import models, fields, api

class courrier_mode_reception(models.Model):
	_name = 'courrier.mode'

	name = fields.Char(string="Mode reception", required=True)


