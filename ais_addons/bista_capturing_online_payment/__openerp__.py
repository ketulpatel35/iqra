# -*- coding: utf-8 -*-

{
    'name': 'Bista Capturing Online Payment',
    'version': '1.0',
    'category': 'Bista Education',
    "sequence": 8,
    'summary': 'Manage Online Payment',
    'complexity': "easy",
    'description': """
            This module use to Capturing Online Payment.
    """,
    'author': 'Bista Solutions',
    'website': 'bistasolutions.com',
    'images': [],
    'depends': ['base', 'bista_edu','bista_strike_off','bista_edu_re_registration','bista_transfer_certificate'],
    'data': [
        'security/ir.model.access.csv',
        'view/payfort_config.xml',
        'view/payfort_payment_capture_view.xml',
        'view/payfort_error_capture.xml',
        'view/menu_view.xml',
        'view/payfort_payment_error_templet.xml',
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
