# -*- coding: utf-8 -*-
{
    'name': "SPEC Utils",

    'summary': """
        Collection of utils components
    """,

    'description': """
        Contains custom reusable components (Fields, Widgets,...)
    """,

    'author': "Dridi <mohamed.elfateh.dridi@spectrumgroupe.fr>",
    'website': "https://spectrumgroupe.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'hr_expense'],

    'external_dependencies': {
        "python": [],
        "lib": []
    },

    # always loaded
    'data': [
        'views/assets.xml',
        'views/hidden_menus.xml',
        'views/menu_icons.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
