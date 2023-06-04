# -*- coding: utf-8 -*-
# Part of AS Consulting


{
    'name': 'Comptabilité - Tunisie',
    'version': '2.0',
    'category': 'Localization',
    'author': 'As Consulting',
    'description': """
This is the module to manage the accounting chart for Tunisia in Odoo.
""",
    'depends': [
        'account'
    ],
    'data': [
        'data/l10n_tn_chart_data.xml',
        'data/account.account.template.csv',
        'data/account_chart_template_data.xml',
        'views/l10n_tn_view.xml',
        'data/account_data.xml',
        'data/tax_report_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_template_data.xml',
        'data/account_chart_template_configure_data.xml',
    ],
}
