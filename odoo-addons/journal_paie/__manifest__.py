# -*- coding: utf-8 -*-
{
    'name': "Tunisie - Journal de Paie",
    'summary':
        """
        Rapport journal de paie tunisien
        """,
    'description':
        """
        Rapport Journal de Paie
        """,
    'category': 'Paie',
    'version': '0.1',
    'depends': ['base', 'om_hr_payroll', 'spc_hr_payroll'],
    'data': [
        'wizards/wizard_recap_paie.xml',
        'report/template_recap_paie.xml',
    ],
    # only loaded in demonstration mode
}
