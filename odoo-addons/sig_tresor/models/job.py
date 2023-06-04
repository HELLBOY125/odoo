# -*- coding:utf-8 -*-

from odoo import models, fields


class Job(models.Model):
    _inherit = 'hr.job'
    _name = 'hr.job'

    delai_traitement_etude_fond = fields.Integer('Délai de traitement',
                                                 help="Entrez ici le délai de traitement de l\'étude de fond du dossier de demande d\'agrément",
                                                 required=True, default=1)
    interne = fields.Boolean('Poste interne', help="Dites si le poste créé est interne à la compagnie", required=True,
                             default=True)
