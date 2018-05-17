# -*- coding: utf-8 -*-

{
    'name': 'Bista Education Strike-off Student',
    'version': '1.0',
    'category': 'Bista Education',
    "sequence": 4,
    'summary': 'Manage Student strike-off',
    'complexity': "easy",
    'description': """
            This module provide strike-off student management system over OpenERP
    """,
    'author': 'Bista Solutions',
    'website': 'bistasolutions.com',
    'images': [],
    'depends': ['base', 'bista_edu'],
    'data': [
        'security/strike_off_security.xml',
        'security/ir.model.access.csv',
        'view/strike_off_student_view.xml',
        'view/strike_off_history_view.xml',
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
