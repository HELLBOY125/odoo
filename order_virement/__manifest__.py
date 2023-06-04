# -*- coding: utf-8 -*-
# -$- Dahech Haithem

###############################################################################
{
    'name': 'Order de Virement ',
    'summary': 'Order de Virement',
    'version': '13.0',
    'description': """Order de Virement""",
    'author': 'BEN MANSOUR Brahim , Dahech Haithem',
    'website': 'http://www.teamit.tn',
    'license': 'AGPL-3',
    'category': 'Payroll',
    'depends': [
        'base','hr','spc_hr_payroll'
    ],
    'data': [
        'views/order_virement_view.xml',
        'report/report_ordre_virement.xml',
        'security/ir.model.access.csv',

    ],
     'installable': True,
    'application': True,
    'auto_install': False,
}
