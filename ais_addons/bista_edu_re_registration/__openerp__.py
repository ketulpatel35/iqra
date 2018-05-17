# -*- coding: utf-8 -*-
#/#############################################################################

#/#############################################################################

{
    'name': 'Bista Education Re-Registration',
    'version': '1.0',
    'category': 'Bista Education',
    "sequence": 5,
    'summary': 'Manage Student Re-Registration Process',
    'complexity': "easy",
    'description': """
    """,
    'author': 'Bista Solutions',
    'website': 'www.bistasolutions.com',
    'images': [],
    'depends': ['base','bista_edu_masters','bista_edu','bista_edu_fee','bista_strike_off','bista_promotion'],
    'data': [
            'view/re_registration_load_js_css.xml',
            'wizard/move_tc_expected_awaiting_fee.xml',
            'wizard/send_for_re_registration.xml',
            'wizard/send_reminder_re_registration.xml',
            'wizard/re_reg_pay_manualy_wizard_view.xml',
            'wizard/reconsile_advance_payment.xml',
            'view/re_regi_waitting_responce_view.xml',
            'view/re_reg_templet.xml',
            'view/batch_view.xml',
            'view/sequence_view.xml',
            'view/email_templet.xml',
            'view/awaiting_re_registration_fee.xml',
            'view/re_registration_workflow.xml',
            'view/tc_expected_view.xml',
            'view/re_registration_fee_voucher_view.xml',
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
