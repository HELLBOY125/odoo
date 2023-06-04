# -*- coding:utf-8 -*-

import logging

from odoo import models, fields, api
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SigTresorTypeIndicateur(models.Model):
    _name = 'sig.tresor.type.indicateur'
    _description = 'type indicateur'
    _rec_name = "name"

    code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_code_type_indicateur(), )
    name = fields.Char(string='Nom', required=True)
    abbreviation = fields.Char(string='Abréviation')
    act_ids = fields.One2many('sig.tresor.activite', 'type_ind_id', 'Activités')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _("Le nom doit être unique !")),
    ]

    @api.model
    def _get_default_code_type_indicateur(self):
        """
        ramène le code suivant du type indicateur
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.type.indicateur')
        print('code %s ' % code)
        return code


class SigTresorActivite(models.Model):
    _name = 'sig.tresor.activite'
    _description = 'activité'
    _rec_name = "name"

    type_ind_id = fields.Many2one('sig.tresor.type.indicateur', 'Type indicateur', required=True)
    code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_code_activite(), )
    name = fields.Char(string='Nom', required=True)
    ind_ids = fields.One2many('sig.tresor.indicateur', 'act_id', 'Indicateurs')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _("Le nom doit être unique !")),
    ]

    @api.model
    def _get_default_code_activite(self):
        """
        ramène le code suivant du activite
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.activite')
        print('code %s ' % code)
        return code


class SigTresorIndicateur(models.Model):
    _name = 'sig.tresor.indicateur'
    _description = 'Indicateur'
    _rec_name = "name"

    type_ind_id = fields.Many2one('sig.tresor.type.indicateur', 'Type indicateur', required=True)
    act_id = fields.Many2one('sig.tresor.activite', 'Activité', required=True)
    code = fields.Char(string='Code', required=True, default=lambda self: self._get_default_indicateur_code(), )
    name = fields.Char(string='Nom', required=True)
    abbreviation = fields.Char(string='Abréviation')
    data_source = fields.Selection([('query', 'Configuration (Query)')],
                                   string='Source de données', required=True, default='query')
    model_id = fields.Many2one('ir.model', 'Table Source')
    model = fields.Char(related='model_id.model', readonly=True)
    field_id = fields.Many2one('ir.model.fields', 'Champs Source',
                               domain="[('store', '=', True), ('model_id', '=', model_id)]") #, ('ttype', 'in', ['float','integer','monetary'])

    calcul_mode = fields.Selection([('count', 'Nombre'), ('sum', 'Somme'),
                                    ('average', 'Moyenne')], string='Mode de calcul', required=True, default='sum')
    frequence = fields.Selection([('monthly', 'Mensuelle'), ('quarterly', 'Trimestrielle'),
                                  ('annual', 'Annuelle')], string='Fréquence', required=True, default='quarterly')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _("Le nom doit être unique !")),

    ]

    @api.model
    def _get_default_indicateur_code(self):
        """
        ramène le code suivant de l'indicateur
        :return:
        """
        code = self.env['ir.sequence'].next_by_code('sig.tresor.indicateur')
        print('code %s ' % code)
        return code

    @api.onchange('type_ind_id')
    def onchange_type_ind_id(self):
        if self.type_ind_id:
            self.type_ind_id = self.type_ind_id.id
            print("type selected %s" % self.type_ind_id)
            res = {}
            res['domain'] = {'act_id': [('type_ind_id', '=', self.type_ind_id.id)]}
            logging.info('LISTE DES ACTIVITES DE L\'INDICATEUR CHOISI')
            logging.info(res)
            return res
