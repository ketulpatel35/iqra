# -*- coding: utf-8 -*-


{
    'name': 'Bista PDC Managment',
    'version': '1.0',
    'category': 'Bista PDC Managment',
    "sequence": 6,
    'summary': 'Manage post date cheque',
    'complexity': "easy",
    'description': """
            This module provide PDC cheque management
    """,
    'author': 'Bista Solutions',
    'website': 'bistasolutions.com',
    'images': [],
    'depends': ['base','account','account_voucher','bista_edu','bista_edu_fee'],
    'data': [
             'pdc_detail_view.xml',
             'wizard/bounce_reason_view.xml',
             'account_voucher_payment_view.xml',
             'wizard/post_cheque_wiz_view.xml',
             'wizard/clear_cheque_wiz_view.xml',
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