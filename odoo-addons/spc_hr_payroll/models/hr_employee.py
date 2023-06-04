# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta, timezone, date
import datetime
from odoo.exceptions import ValidationError, UserError


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    matricule_cnss = fields.Char(string='Matricule CNSS')
    house_holder = fields.Boolean(string='Chef de famille', default=False)
    infirme = fields.Boolean(string='Enfant infirme', default=False)
    student = fields.Boolean(string='Enfant étudiant', default=False)
    delivred_date_identification = fields.Date(string="Délivrée le")

    @api.constrains('matricule_cnss')
    def _check_num_securite_sociale(self):
        for record in self:
            if record.matricule_cnss:
                if not record.matricule_cnss.isdecimal():
                    raise ValidationError("Le N° de  sécurité sociale ne doit contenir que des chiffres !")
                if len(record.matricule_cnss) > 20:
                    raise ValidationError(
                        "Le longeur du N° de sécurité sociale ne doit pas être supérieur à 20 chiffres!")
