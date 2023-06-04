# -*- coding:utf-8 -*-

from odoo import models, fields


class SigTresorLegalForm(models.Model):
    _name = 'sig.tresor.legal.form'
    _description = 'Forme Juridique'
    _rec_name = "legal_form_name"  # string value display form agreement request
    _order = 'legal_form_name desc'

    legal_form_name = fields.Char("Nom", required=True)
    legal_form_description = fields.Text("Description")
    legal_form_abbreviation = fields.Char("Abréviation", size=50)
    legal_form_code = fields.Char("Code", size=1, required=True)
    is_required_no_rccm = fields.Boolean("N° RCCM est obligatoire")


class SigTresorMutualSpecificity(models.Model):
    _name = 'sig.tresor.mutual.specificity'
    _description = 'Spécificité Mutuelle'
    _rec_name = "mutual_specificity_name"  # string value display form agreement request
    _order = 'mutual_specificity_name desc'

    mutual_specificity_name = fields.Char("Nom", required=True)
    mutual_specificity_description = fields.Text("Description")
    mutual_specificity_code = fields.Char("Code", size=2)
    legal_form_id = fields.Many2one('sig.tresor.legal.form', 'Forme Juridique')


class SigTresorTypeCourrier(models.Model):
    _name = 'sig.tresor.type.courrier'
    _description = 'Type Courrier'
    _rec_name = "type_courrier_name"  # string value display form agreement request
    _order = 'type_courrier_name desc'

    type_courrier_name = fields.Char("Nom", required=True)
    type_courrier_description = fields.Text("Description")
    type_courrier_state = fields.Selection([('recept_enr', 'Réception & Enregistrement'),
                              ('etude_forme', 'Etude de forme'),
                              ('etude_fond', 'Etude de fond'),
                              ('saisine_bceao', 'Saisine BCEAO')],
                             string="Étape", default='recept_enr', required=True)
