# -*- coding: utf-8 -*-
{
    "name": "Bureau d'ordre",
    "description": """
BUREAU D'ORDRE
========================
Ce module gère les courriers entrants et sortants d'un bureau d'ordre. 
""",
    "author": "SPECTRUM GROUPE",
    "version": '0.1',
    "depends": ['base', 'mail', 'hr'],

    # always loaded
    "data": [
        "security/bo_security.xml",
        "security/ir.model.access.csv",
        "data/courrier_urgence_data.xml",
        
        'data/courrier_type_data.xml',
        'data/bureau_ordre_data.xml',
        "data/mode_data.xml",
         "views/urgence.xml",

        "views/courrier_entrant_view.xml",
        "views/courrier_sortant_view.xml",

        "views/type_courrier.xml",
        "views/mode_reception_view.xml",
        "views/steg_department.xml",
    ],
}