# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class TransferCertificateInheritPayfort(models.Model):

    _inherit = 'trensfer.certificate'

    @api.model
    def _get_payfort_payment_link(self,amount,order_id):
        """
        Genarate link for online payfort payment.
        ----------------------------------------
        :return:
        """
        link = '/redirect/payfort?AMOUNT=%s&ORDERID=%s'%(amount,order_id)
        return link