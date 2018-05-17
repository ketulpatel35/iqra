# -*- coding: utf-8 -*-


{
    'name': 'Bista Education Student Promotion',
    'version': '1.0',
    'category': 'Bista Education',
    "sequence": 4,
    'summary': 'Manage Student Promotion',
    'complexity': "easy",
    'description': """
            This module provide student promotion system over OpenERP
    """,
    'author': 'Bista Solutions',
    'website': 'bistasolutions.com',
    'images': [],
    'depends': ['base', 'bista_edu', 'bista_edu_fee','bista_strike_off'],
    'data': [
        'wizard/awaiting_promotion_wiz.xml',
        'view/email_template.xml',
        'view/awaiting_promotion.xml',
        'view/confirm_fees_structure_view.xml',
        'view/alumni_student_view.xml',
        'view/promotion_view.xml',
        'view/menu_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'test': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
