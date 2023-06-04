# -*- coding: utf-8 -*-
{
    'name': 'SPECTRUM - Paie TN',
    'category': 'Payroll/Localisation',
    'website': 'https://spectrumgroupe.fr',
    "category": "Payroll",
    'version': '1.1',
    'depends': ['om_hr_payroll', 'hr_holidays'],
    'description': """Tunisian Payroll Rules For Active Contact.
========================================================================
**Credits:** .

   Gestion de la Paie Tunisienne:    
    - Gestion des employés.
    - Gestion des contrats.
    - Configuration et paramètrage
            * Les rubriques de paie :primes,indemnités,avantages,déductions,...
            * Les rubriques cotisable ,imposable , soumise à la prime d'ancienneté  ...
            * Les cotisations : cotisations salariales et patronales CNSS,Mutuelle...
            * Barème de la prime d'ancienneté,cotisations CNSS ...       
    - Calcul de paie selon les normes tunisien : calcul automatique de la prime d'ancienneté,heures supplémentaire,cotisations salariales et patronales,...
    - Gestion des congés  : Calcul automatique des congés non payés à partir du module hr_holidays
    - Reporting : les  bulletins de paie,journale de paie ,Ordres de virement ...
    """,
    'active': False,
    'data': [
        'security/ir.model.access.csv',
        'data/hr_employee_category_data.xml',
        'data/hr_payroll_structure.xml',
        'report/report_payslip_templates.xml',
        'views/hr_convention_views.xml',
        'views/hr_premium_views.xml',
        'views/hr_payroll_views.xml',
        'views/hr_contract_views.xml',
        'views/res_company.xml',
        'wizard/views/hr_premium_rules_wizard_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,


}
