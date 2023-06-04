# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sig Tresor',
    'author': 'VEONE',
    'website': "http://www.veone.net",
    "support": "support@veone.net",
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    "category": "project",
    "images": ['static/description/icon.png'],
    'summary': """
        Système Intégré de Gestion pour le TRESOR de Côte d'Ivoire
    """,
    'description': """
Système Intégré de Gestion pour le TRESOR de Côte d'Ivoire
==========================================================
""",
    # any module necessary for this one to work correctly
    'depends': ['web', 'base', 'hr', 'mail'],
        
    # always loaded
    'data': [
        "security/sig_tresor_groups.xml",
        'security/ir.model.access.csv',
        'data/sig_tresor_sequence.xml',
        'data/specificite_data.xml',
        #"template/sig_tresor_template.xml",
        "views/sig_tresor_menus.xml",
        # "security/sig_tresor_security.xml",
        "views/sig_tresor_specific_view.xml",
        "views/sig_tresor_location_view.xml",
        "views/sig_tresor_indicateur_view.xml",
        "views/sig_tresor_commentaire_view.xml",
        "wizard/historique_view.xml",
        # "workflow/demande_agrement/sig_tresor_reception_courrier_view.xml",
        # "workflow/demande_agrement/sig_tresor_verif_conformite_dossier_view.xml",
        # "workflow/demande_agrement/sig_tresor_etude_fond_dossier_view.xml",
        # "workflow/demande_agrement/sig_tresor_saisine_bceao_view.xml",
        # "views/sig_tresor_dirigeant_view.xml",
        # 'email/notification_email.xml',
        "views/cmis.xml",
        'views/historique_report.xml',
        'data/specificite_data.xml',
        
    ],
    # "qweb": ['static/src/xml/mask.xml'],
    "update_xml": [
        'views/user_view.xml',
        "views/job_view.xml",
        "views/employee_view.xml",
        # "views/partner_view.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        # "data/sig_tresor_location_data.xml",
        # "data/sig_tresor_specific_data.xml",
        "demo/sig_tresor_cmis.xml",
    ],
    'test': [],
    'installable': True,
    "auto_install": False,
    'application': True,
}
