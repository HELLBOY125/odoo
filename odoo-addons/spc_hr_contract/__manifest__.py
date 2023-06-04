# -*- coding: utf-8 -*-
{
    'name': 'Contrats des Employés',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
Ajoutez toutes les informations relatives aux employés pour gérer les contrats.
=============================================================

    * Contrat
    * Date de naissance
    * Date de l'examen médical
    * Véhicule de société

Vous pouvez attribuer plusieurs contrats par employé.
    """,
    'website': 'https://www.odoo.com/page/employees',
    'author': 'Saif Eddine ISSAOUI',
    'depends': ['base', 'hr', 'hr_contract', 'hr_contract_types', 'intl_tel_widget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/contract_type_data.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/res_company.xml',
        'reports/layouts.xml',
        'reports/employee_contract_cdi_cdd.xml',
        'reports/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}