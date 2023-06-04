# -*- coding: utf-8 -*-

{

    'name': "Congés",

    'summary': """Spectrum Groupe Leaves""",

    'description': """
        spc leaves module for leaves management:
            - employee
            - conge
    """,

    'author': "Spectrum Groupe",
    'website': "https://spectrumgroupe.fr/",
    'images': [
        'static/description/icon.png',
    ],


    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','spc_hr','hr_holidays','hr_holidays_calendar', 'resource'],

    # always loaded
    'data': [
        
        'data/hr_holidays_data.xml',
        'data/email_template.xml',
        'security/ir.model.access.csv',
        'views/leaves_view.xml',
        'views/res_config_settings_views.xml',
        'views/hr_leave_allocation.xml',
        'views/hr_leave_allocation_accruement.xml',
        'views/hidden_menus.xml',
        'report/leave_report.xml',
        'report/report_leave.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
