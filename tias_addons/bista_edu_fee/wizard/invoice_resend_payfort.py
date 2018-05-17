from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import hashlib

class ResendPayfortLink(models.TransientModel):

    _name='invoice.resend.payfort'

    @api.multi
    def resend_payfort_link(self):
        invoice_obj = self.env['account.invoice']
        active_ids=self._context['active_ids']

        for invoice_rec in invoice_obj.browse(active_ids):

            # send payfort link
            active_payforts=self.env['payfort.config'].search([('active','=','True')])

            if len(active_payforts) > 1:
                raise except_orm(_('Warning!'),_("There should be only one payfort record!"))

            if not active_payforts.id:
                raise except_orm(_('Warning!'),_("Please create Payfort Details First!"))

            payfort_amount = invoice_rec.residual
            if active_payforts.charge != 0.00:
                payfort_amount += (payfort_amount*active_payforts.charge)/100

            total_amount = str(int(round(payfort_amount * 100)))

            invoice_number = invoice_rec.number
            SHA_key = active_payforts.sha_in_key
            PSP_ID = active_payforts.psp_id
            string_input = 'AMOUNT=%s' % (total_amount) + SHA_key + 'CURRENCY=AED' + SHA_key + 'LANGUAGE=EN_US' + SHA_key + 'ORDERID=%s' % (invoice_number) + SHA_key + 'PSPID=%s'%(PSP_ID) + SHA_key
            ss='AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s'%(total_amount,invoice_number,PSP_ID)

            m = hashlib.sha1()
            m.update(string_input)
            hashkey=m.hexdigest()
            hashkey=hashkey.upper()
            link = str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss,hashkey,)

            # resend mail to the parent
            if invoice_rec.partner_id.is_parent == False:
                mail_obj = self.env['mail.mail']
                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([],limit=1)
                mail_data={
                   'email_from':email_sender.smtp_user,
                   'email_to':invoice_rec.partner_id.parents1_id.parents_email,
                   'subject':'Resend Academic Fee Payment Link',
                   'body_html':'<div><p>Dear %s,</p> </br>'
                           '<p><a href=%s>Click Hear</a> to pay monthaly Acd Fees</p>'
                           '<p>Best Regards<br/>'
                            'Registrar<br/>'
                            'The Indian Academy, Sharjah</p>' % (invoice_rec.partner_id.parents1_id.name,link)
                    }
                mail_id = mail_obj.create(mail_data)
                mail_obj.send(mail_id)
