# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Process médecin",
    'version': '0.1',
    'category': 'Base',
    'author': 'Redid Sihem - Spectrum Groupe',
    'summary': "Process médecin dans l'achat conventionée",
   
    'description': """
      Ajouter le note d'honoraires du médecin
    
    """,
    'depends': ['base','hr','spc_supplier_partner'],
    'data': [ 
              
              'security/ir.model.access.csv',
              'data/type_medecin_data.xml',
              'views/res_partner_medecin_view.xml',
              'views/res_partner_view.xml',
              'views/res_vacation_config_view.xml',
             
              ],
    'installable': True,
}
