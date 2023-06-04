# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Convention d'achat",
    'version': '0.1',
    'category': 'Operations/Purchase',
    'author': 'Redid Sihem - Spectrum Groupe',
    'summary': "Convention d'achat",

    'description': """
        Conventions Personnes physiques : Adhérent
        Conventions Personnes libérales : Pharmacies, Laboratoires d'analyse, centre de radiologie
        Conventions Personnes libérales : Médecins,
        Conventions Personne physique : Cliniques ou hôpitaux
    """,
    'depends': ['base',
                 'purchase', 
                 'mail',
                 'account',
                 'spc_supplier_partner',
                 'spc_hr',
                 'spc_process_medecin'],
    'data': [
        'data/data.xml',
        'data/ir_cron_data.xml',
        'security/contracted_purchase_security.xml',
        'security/ir.model.access.csv',
        'wizard/resiliation_wizard_view.xml',
        'wizard/add_invoice_view.xml',
        'views/categorie_purchase_agreement_views.xml',
        'views/purchase_agreement_article_views.xml',
        'views/purchase_agreement_views.xml',
        'views/agreement_resiliation_views.xml',
        'views/purchase_agreement_report.xml',
        'views/purchase_agreement_resialition_report.xml',
        'views/account_invoice_views.xml',
        'views/bs_views.xml',
        'views/prise_charge_views.xml',
        'views/process_medecin_views.xml',
        'views/lettre_pharmacie_report.xml',
        'views/ordre_retenue_pharmacie_report.xml',
        'views/ordre_retenue_adherent_report.xml',
        'views/report_payment_receipt_templates.xml',
        'views/menu_views.xml',
        'views/check_reason_view.xml'
    ],
    'installable': True,
}