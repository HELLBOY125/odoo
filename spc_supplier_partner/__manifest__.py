# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Fournisseur',
    'version': '0.1',
    'category': 'base',
    'author': 'Redid Sihem - Spectrum Groupe',
    'summary': 'Ajouter des champs au fournissuer',
   
    'description': """
    
    """,
    'depends': ['base'],
    'data': [ 'security/ir.model.access.csv',
              'views/res_speciality_view.xml',
              'views/res_partner_view.xml',
              ],
    'installable': True,
}
