# -*- coding: utf-8 -*-
{
    'name': 'Employés',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Centralisez les informations des employés',
    'description': "",
    'website': 'https://www.odoo.com/page/employees',
    'version': '0.1',
    'author' : 'Saif Eddine ISSAOUI',
    'images': [
        'static/description/icon.png',
    ],


    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'spc_res_partner', 'intl_tel_widget', 'spc_hr_contract'],

    # always loaded
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'data/employee_type_data.xml',
        'data/tn_states_data.xml',
        'views/res_partner_bank_view.xml',
        'views/company_view.xml',
        'views/hr_view.xml',
        'views/hr_employee_type.xml',
        'views/hr_work_location.xml',
        'views/hr_job.xml',
        'views/res_config_settings.xml',
        'views/hidden_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}