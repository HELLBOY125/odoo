# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Job(models.Model):
    _inherit = "hr.job"

    job_description = fields.Html(string="Fonction et attributions")