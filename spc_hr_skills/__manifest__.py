# -*- coding: utf-8 -*-
{
    'name': 'Gestion des compétences',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Centralisez les informations pour gérer les compétences',
    'description': "",
    'website': '',
    'version': '0.1',
    'author' : 'Mohamed Amine Kaabi',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_skills', 'spc_hr', 'spc_res_partner'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/university_view.xml',
        'views/hr_view.xml',
        'views/hr_employee_diploma.xml',
        'views/ir_attachment_view.xml',
        'data/hr_resume_data.xml',
    ],

    'qweb': [
        'static/src/xml/resume_templates.xml',
    ],

}