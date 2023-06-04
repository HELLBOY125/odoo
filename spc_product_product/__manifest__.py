# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Nature Article',
    'version': '0.1',
    'category': 'Products',
    'author': 'Redid Sihem - Spectrum Groupe',
    'summary': 'Nature article',
   
    'description': """
      Ajout nature d'article :

        1-Fournitures
        2-Medicaments
        3-Actes
     Ajout quelque selon Nature d'article
    """,
    'depends': ['product'],
    'data': [ 
              'views/product_view.xml',
              ],
    'installable': True,
}
