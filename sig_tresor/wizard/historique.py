# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions
from datetime import date


class SigTresorHistorique(models.TransientModel):
    _name = 'sig.tresor.historique'
    _rec_name = "wkf_nom"

    wkf_nom = fields.Selection([('DA', 'Demande d\'Agrément'),
                              ('RA', 'Rétrait d\'Agrément'),
                              ('AD', 'Autorisation Diverses'),],
                             string="Processus", default='DA', required=True, readonly=True)
    wkf_etat = fields.Selection([('forme', 'Etude de forme'),
                                ('fond', 'Etude de fond'),
                                ('saisine', 'Saisine'), ],
                               string="Etat", default='forme', required=True, readonly=True)
    date_reception = fields.Datetime('Date réception', required=True)
    date_transmission = fields.Datetime('Date transmission', required=True)
    delai = fields.Integer('Délai', compute='_compute_delai', store=True, required=True)

    @api.depends('date_reception', 'date_transmission')
    def _compute_delai(self):
        if self.date_reception and self.date_transmission:
            self.delai = (self.date_transmission - self.date_reception).days


    def action_historiser(self):
        """
        Historiser les délai et dates pour la BI
        :return:
        """
        vals = {
            'wkf_nom': self.wkf_nom,
            'wkf_etat': self.wkf_etat,
            'date_reception': self.date_reception,
            'date_transmission': self.date_transmission,
            'delai': self.delai,  # (self.date_transmission-self.self.date_reception).days,
           }
        self.env['sig.tresor.historique'].create(vals)
        return True