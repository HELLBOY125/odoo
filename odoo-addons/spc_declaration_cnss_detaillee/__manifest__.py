# -*- coding: utf-8 -*-
#__ developed by Dahech Haithem
{
    'name': "Tunisie - Declaration CNSS Detaillee",

    'summary': """
       Rapport Declaration CNSS Detaillee""",

    'description': """
        Report Declaration CNSS Detaillee
    """,

    'category': 'payroll',
    'version': '13.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'spc_hr_payroll', 'spc_declaration_cnss'],

    # always loaded
    'data': [
        'views/template_declaration_cnss_det_hr.xml',
        'views/wizard_empl_view.xml',
    ],
    # only loaded in demonstration mode

}
