# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from odoo.exceptions import  UserError
from odoo.osv import expression

class ResPartnerMedecin(models.Model):
    _name = 'res.partner.medecin'
    _description="Type"
    
    name = fields.Char(string='Type')
    type = fields.Selection([('medecin','Médecin'),('vacataire','Vacataire')],default='medecin',required="1")

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _get_type(self):
        type_id =self.env['res.partner.medecin'].sudo().search([('type','=',self.env.context.get('default_type_medecin'))],limit=1)
        return type_id
   
    is_vacataires = fields.Boolean(help="Cochez cette case si ce contact est un vacatiare.")
    is_medecin = fields.Boolean(help="Cochez cette case si ce contact est un médecin.")
    type_medecin_id = fields.Many2one('res.partner.medecin',string='Type de médecin',default=_get_type)

class ResVacationConfig(models.Model):
    _name = 'res.vacation.config'
    _description="Vacation par spécialité"
    _rec_name='type_medecin_id'
    
    
    type_medecin_id = fields.Many2one('res.partner.medecin',string='Type de médecin')
    number_vacation_limite = fields.Integer(string="Nombre des malades par vacation")
    tarif =fields.Float(string='Tarif par Vacation')
     