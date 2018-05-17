# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api, _

class payfort_config(models.Model):

    _name = 'payfort.config'

    name = fields.Char(string="Name",size=126)
    sha_in_key = fields.Char(string="SHA In key",size=126)
    charge = fields.Float(string='Charge(%)')
#    test = fields.Boolean(string="Is Test")
    active = fields.Boolean(string="Active")
    transaction_charg_amount = fields.Float('Transaction Charges')
    payfort_type = fields.Selection([('test','Test'),('production','Production')],string='Payfort Type')
    payfort_url = fields.Char(compute="_payfort_type_url",string='Payfort Url',store=True)
    psp_id = fields.Char('PSP ID')
    journal_id = fields.Many2one('account.journal','Payment Method')

    @api.one
    @api.depends('payfort_type')
    def _payfort_type_url(self):
        if self.payfort_type == 'test':
            self.payfort_url = 'https://secure.payfort.com/ncol/test/orderstandard.asp'
        elif self.payfort_type == 'production':
            self.payfort_url = 'https://secure.payfort.com/ncol/prod/orderstandard.asp'

    @api.one
    @api.depends('payfort_type')
    def _payfort_type_url(self):
        if self.payfort_type == 'test':
            self.payfort_url = 'https://secure.payfort.com/ncol/test/orderstandard.asp'
        elif self.payfort_type == 'production':
            self.payfort_url = 'https://secure.payfort.com/ncol/prod/orderstandard.asp'