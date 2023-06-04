# -*- coding: utf-8 -*-
{
    'name': "Tunisie - Declaration CNSS",

    'summary': """""",

    'description': """
        Report Declaration CNSS sur fichier txt
    """,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'spc_hr_payroll'],

    # always loaded
    'data': [
        'views/declaration_cnss_view.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode

}
