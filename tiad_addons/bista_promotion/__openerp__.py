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
    'depends': ['base','bista_edu'],
    'data': [
        'view/email_template.xml',
        'view/alumni_student_view.xml',
        'view/confirm_fee_structure_view.xml',
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
