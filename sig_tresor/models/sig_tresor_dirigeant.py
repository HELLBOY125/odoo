# -*- coding:utf-8 -*-

from odoo import models, fields


class SigTresorDirigeant(models.Model):
    _name = 'sig.tresor.dirigeant'
    _description = 'Dirigeant'

    nom = fields.Char('Nom', required=True)
    email = fields.Char('Email', required=True)
    telephone = fields.Char('Téléphone', required=True)
    job_id = fields.Many2one("hr.job", 'Poste Occupé', domain=lambda self: [("interne", "=", False)], required=True)
    verif_conformite_dossier_id = fields.Many2one("sig.tresor.verif.conformite.dossier", "Dossier",
                                                  required=True, domain=lambda self: [
            ("reception_courrier_id.etape", "=", "recep_enr_dossier")])
