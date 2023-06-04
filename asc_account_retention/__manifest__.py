# -*- coding: utf-8 -*-
# Part of AS Consulting


{
    'name': 'Retenue à la source',
    'version': '2.0',
    'category': 'Tunisian Accounting',
    'author': 'As Consulting',
    'description': """
Comptabilité - Tunisie - Retenue à la source
""",
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/asc_account_retention_view.xml',
        'views/asc_account_payment_view.xml',
        'views/asc_partner_view.xml',
        
        'views/asc_report.xml',
        #'views/asc_retention_report.xml',
        'views/certificat_retenue_templates.xml'
    ],
}
