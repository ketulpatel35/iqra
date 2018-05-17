from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
import base64
from openerp import models, fields, api, _
import time
from openerp.addons.bista_edu.Controllers.main import payfort_payment_status as bista_edu_show_acd_payment

class payfort_payment_status_inherit(bista_edu_show_acd_payment):

    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use to online payment by student/parent
        for TC Fee and outstading balance..
        ---------------------------------------------------
        :param post:
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        tc_student_rec = env['trensfer.certificate'].sudo().search([('code', '=', post['orderID'])],limit=1)
        if len(tc_student_rec) > 0:
            if post['STATUS'] == '9':
                voucher_obj = env['account.voucher']
                voucher_line_obj = env['account.voucher.line']
                period_rec = self._get_period()
                payment_id = post['PAYID']
                curency_id = self._get_currency()
                amount = post['amount']
                orignal_amount = self.get_orignal_amount(amount)
                current_date = time.strftime('%Y-%m-%d')
                order_id = post['orderID']
                voucher_rec = voucher_obj.search([('payfort_payment_id', '=', payment_id),('reference', '=', order_id)],
                                                 limit=1)
                journal_id = self.get_journal_from_payfort()
                if not voucher_rec.id:
                    voucher_data = {
                        'period_id': period_rec.id,
                        'account_id': env['account.journal'].browse(journal_id).default_debit_account_id.id,
                        'partner_id': tc_student_rec.name.id,
                        'journal_id': journal_id,
                        'currency_id': curency_id,
                        'reference': order_id,
                        'amount': orignal_amount,
                        'type': 'receipt' or 'payment',
                        'state': 'draft',
                        'pay_now': 'pay_later',
                        'name': '',
                        'date': current_date,
                        'company_id': 1,
                        'tax_id': False,
                        'payment_option': 'without_writeoff',
                        'comment': _('Write-Off'),
                        'payfort_payment_id': payment_id,
                        'payfort_pay_date': current_date,
                    }
                    voucher_rec = voucher_obj.sudo().create(voucher_data)
                    res_line_ids = voucher_rec.onchange_partner_id(voucher_rec.partner_id.id, journal_id,
                                          orignal_amount,
                                          voucher_rec.currency_id.id,
                                          voucher_rec.type, current_date)

                    for line_data in res_line_ids['value']['line_cr_ids']:
                        voucher_lines = {
                            'move_line_id': line_data['move_line_id'],
                            'amount': line_data['amount_unreconciled'] or line_data['amount'],
                            'name': line_data['name'],
                            'amount_unreconciled': line_data['amount_unreconciled'],
                            'type': line_data['type'],
                            'amount_original': line_data['amount_original'],
                            'account_id': line_data['account_id'],
                            'voucher_id': voucher_rec.id,
                            'reconcile': True
                        }
                        voucher_line_obj.sudo().create(voucher_lines)

                    # Validate voucher (Add Journal Entries)
                    voucher_rec.button_proforma_voucher()
                    tc_student_rec.send_fee_receipt_mail(voucher_rec)
                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {'pay_id':post['PAYID']})
                else:
                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {'pay_id':post['PAYID']})
        res = super(payfort_payment_status_inherit,self).show_acd_payment(**post)
        return res

class TrensferCertificateController(http.Controller):

    def decode_base64(self,data):
        """
        Decode base64, padding being optional.
        ------------------------------------------------
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
        """
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += b'='* missing_padding
        try:
            res = base64.decodestring(data)
            if res:
                return res
        except:
            return ''

    @http.route([
        '/student/tc/request',
    ], type='http', auth="public", website=True)
    def render_tc_request(self, **post):
        """
        this method is used to call webpage for TC Form.
        When students leave the school, it is through the TC process.
        then this process must be required.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                required data
        """
        env = request.env(user=SUPERUSER_ID)
        if 'TCCODE' in post and post.get('TCCODE'):
            data = post.get('TCCODE')
            tc_code = self.decode_base64(data)
            env = request.env(context=dict(request.env.context, show_address=True,no_tag_br=True))
            tc_object = env['trensfer.certificate']
            tc_stud_record = tc_object.sudo().search([('code','=',tc_code)],limit=1)
            if tc_stud_record.id and tc_stud_record.tc_form_filled != True:
                return request.website.render("bista_transfer_certificate.tc_form_request", {
                    'tc_stud_rec' : tc_stud_record
                    })
            else:
                return request.website.render("bista_transfer_certificate.tc_request_fail", {})
        else:
            return request.website.render("bista_transfer_certificate.tc_request_fail", {})

    @http.route([
    '/student/tc/responce',
    ], type='http', auth="public", website=True)
    def render_student_tc_form_responce(self, **post):
        """
        this method is use for getting responce from parent
        for conformation of tc form.
        :param post:
        :return:
        """
        if post and 'TCCODE' in post and post.get('TCCODE'):
            env = request.env(user=SUPERUSER_ID)
            tc_object = env['trensfer.certificate']
            tc_stud_record = tc_object.sudo().search([('code','=',post.get('TCCODE'))],limit=1)
            if tc_stud_record.id:
                tc_type = ''
                if 'select_type_tc' in post and post.get('select_type_tc'):
                    tc_type = post.get('select_type_tc')
                tc_stud_record.sudo().write({'tc_form_filled' : True,
                                             'new_school_name': post.get('new_school_name'),
                                             'reason_for_leaving':post.get('reason_leaving'),
                                             'tc_type':tc_type})
                if tc_stud_record.tc_form_filled == True:
                    tc_stud_record.sudo().come_to_fee_balance_review()
                return request.website.render("bista_transfer_certificate.tc_request_success", {})
            else:
                return request.website.render("bista_transfer_certificate.tc_request_fail", {})

