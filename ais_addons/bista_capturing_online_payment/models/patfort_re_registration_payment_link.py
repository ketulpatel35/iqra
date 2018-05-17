# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class ReRegistrationResponceParents(models.Model):

    _inherit = 're.reg.waiting.responce.parents'

    @api.model
    def send_re_registration_payment_link(self, parent_record, child_data_table):
        """
        this method is use to send mail to parent for pay
        re-registration fee.
        @overide method : send_re_registration_payment_link (bista_edu_re_registration)
        -------------------------------------------------------------------------------
        :param parent_record: re-registration parent record set
        :param amount: total payable amount
        :return:
        """
        amount = parent_record.residual
        for student_re_rec in parent_record.student_ids:
            if student_re_rec.name.credit > 0.00:
                amount += student_re_rec.name.credit
        link = '/redirect/payfort?AMOUNT=%s&ORDERID=%s'%(amount,parent_record.code)
        link_data = ''
        if amount > 0.00:
            link_data += '<p><a href=%s><button>Click here</button></a> to pay online</a></p>'%(link)
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([], limit=1)
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('bista_edu_re_registration', 'email_template_re_registration_confirmation')[1]
        template_rec = self.env['email.template'].browse(template_id)
        body_html = template_rec.body_html
        body_dynamic_html = template_rec.body_html
        body_dynamic_html += '<table border=1><tr><td><b>Student Name</b></td><td><b>Class-Sec</b></td><td><b>Re-registration confirmation</b></td><td><b>Amount for re-registration</b></td></tr>%s</table>'%(child_data_table)
        body_dynamic_html += '<p>The total payable amount is AED %s(plus applicable online transaction charges)</p>'%(amount)
        body_dynamic_html += '%s</div>'%(link_data)
        template_rec.write({'email_to': parent_record.name.parents_email,
                            'email_from': email_sender.smtp_user,
                            'email_cc': 'Erpemails_ais@iqraeducation.net',
                            'body_html': body_dynamic_html})
        template_rec.send_mail(self.id)
        template_rec.body_html = body_html