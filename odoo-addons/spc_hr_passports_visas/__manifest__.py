# -*- coding: utf-8 -*-
{
    'name': 'Passeports et Visas',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Centralisez les informations des passeports et visas employés',
    'description': "",
    'website': '',
    'version': '0.1',
    'author' : 'Saif Eddine ISSAOUI',

    # any module necessary for this one to work correctly
    'depends': ['base', 'spc_hr', 'spc_utils'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_view.xml',
        'views/hr_passport.xml',
        'views/hr_visa.xml',
        'views/hr_type_visa.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}