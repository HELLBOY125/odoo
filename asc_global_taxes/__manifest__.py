# -*- coding: utf-8 -*-
# Part of AS Consulting


{
    'name': 'Timbre Fiscal',
    'version': '3.0',
    'category': 'Tunisian Accounting',
    'author': 'As Consulting',
    'description': """
Comptabilité - Tunisie - Timbre Fiscal.
""",
    'depends': [
        'account', 'l10n_tn'
    ],
    'data': [
        'views/asc_account_templates.xml',
        'views/res_config_settings.xml',
        'views/asc_account_move_view.xml'
    ],
}
