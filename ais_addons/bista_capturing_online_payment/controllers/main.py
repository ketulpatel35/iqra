from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp import http
from openerp.http import request,db_filter
import hashlib
import flask
from datetime import date
from openerp.addons.bista_edu.Controllers.main import payfort_payment_status as bista_edu_show_acd_payment

class PayfortPaymentLinkRedirect(http.Controller):

    @http.route([
        '/redirect/payfort'
    ], type='http', auth="public")
    def redirect_payfort(self, **post):
        """
        create payfort payment link and
        redirect to Payfort Page.
        -------------------------------
        :return: redirect to payfort payment getway page.
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        payfort_conf_obj = env['payfort.config']
        payfort_conf_rec = payfort_conf_obj.sudo().search([('active', '=', 'True')],limit=1)
        if payfort_conf_rec.id:
            amount = 0.00
            order_id = post.get('ORDERID')
            total_amount = float(post.get('AMOUNT')) or 0.00
            SHA_key = payfort_conf_rec.sha_in_key
            PSP_ID = payfort_conf_rec.psp_id
            payfort_url = payfort_conf_rec.payfort_url
            if payfort_conf_rec.id and payfort_conf_rec.charge != 0:
                    total_amount += (total_amount * payfort_conf_rec.charge) / 100
            if payfort_conf_rec.transaction_charg_amount > 0.00:
                total_amount = total_amount + payfort_conf_rec.transaction_charg_amount
            total_net_amount = round(total_amount,2)
            amount = str(int(total_net_amount * 100))
            string_input = 'AMOUNT=%s' % (
                amount) + SHA_key + 'CURRENCY=AED' + SHA_key + 'LANGUAGE=EN_US' + SHA_key + 'ORDERID=%s' % (
            order_id) + SHA_key + 'PSPID=%s'%(PSP_ID) + SHA_key
            ss = 'AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s' % (amount, order_id, PSP_ID)
            m = hashlib.sha1()
            m.update(string_input)
            hashkey = m.hexdigest()
            hashkey = hashkey.upper()
            link = str(payfort_url) + '?%s&SHASIGN=%s' % (ss, hashkey,)
            return flask.redirect(link,code=302)

class ShowAcdPaymentInheritPayfortCapture(bista_edu_show_acd_payment):

    def calculate_payfort_charges_value(self,paid_amount):
        """
        this method use to calculate payfort charges.
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')],limit=1)
        amount = float(paid_amount)
        bank_charges = 0.00
        transaction_charges = 0.00
        gross_transaction_value = 0.00
        net_amount = 0.00
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.charge > 0.00:
                bank_charges =  (paid_amount * active_payforts_rec.charge)/100
            else:
                bank_charges =  (paid_amount * 2.1)/100
            transaction_charges = active_payforts_rec.transaction_charg_amount
            gross_transaction_value = paid_amount + bank_charges + transaction_charges
            if active_payforts_rec.bank_service_charge > 0.00:
                transaction_charges_deducted_by_bank = \
                    (gross_transaction_value * active_payforts_rec.bank_service_charge) / 100
            else:
                transaction_charges_deducted_by_bank = \
                    (gross_transaction_value * 2.1) / 100
            net_amount = gross_transaction_value - transaction_charges_deducted_by_bank
        else:
            bank_charges = (paid_amount * 2.1) / 100
            transaction_charges = 0.50
            gross_transaction_value = paid_amount + bank_charges + transaction_charges
            transaction_charges_deducted_by_bank = (gross_transaction_value * 2.1) / 100
            net_amount = gross_transaction_value - transaction_charges_deducted_by_bank

        return bank_charges, transaction_charges, gross_transaction_value,\
               net_amount, transaction_charges_deducted_by_bank

    @http.route([
    '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use to online payment by student/parent
        for Re-Registration
        ---------------------------------------------------
        :param post:
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        if not post.get('STATUS') == '9':
            payfort_error_capture_obj = env['payfort.error.capture']
            payfort_error_capture_data = {
                'date' : date.today(),
                # 'partner':partner,
                'pay_id' : post.get('PAYID') or '',
                'reference_number' :  post.get('orderID'),
                'amount' : post.get('amount'),
                'error_message' :  'Payment Transaction could not be Completed. Payment Status is %s'%(post.get('STATUS')),
                'payment_status': post.get('STATUS'),
            }
            payfort_error_capture_obj.sudo().create(payfort_error_capture_data)
            return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
                })
        try:
            res = super(ShowAcdPaymentInheritPayfortCapture,self).show_acd_payment(**post)
        except Exception as err_msg:
            payfort_error_capture_obj = env['payfort.error.capture']
            payfort_error_capture_data = {
                'date' : date.today(),
                # 'partner':partner,
                'pay_id' : post.get('PAYID') or '',
                'reference_number' :  post.get('orderID'),
                'amount' : post.get('amount'),
                'error_message' :  err_msg,
                'payment_status': post.get('STATUS')
            }
            payfort_error_capture_obj.sudo().create(payfort_error_capture_data)
            return request.render("bista_capturing_online_payment.payfort_payment_error_templet", {
                'payment_id':post.get('PAYID'),
                'order_id':post.get('orderID'),
                'err_msg':err_msg,
            })
        except:
            import sys
            err_msg = sys.exc_info()[0]
            payfort_error_capture_obj = env['payfort.error.capture']
            payfort_error_capture_data = {
                'date' : date.today(),
                # 'partner':partner,
                'pay_id' : post.get('PAYID') or '',
                'reference_number' :  post.get('orderID'),
                'amount' : post.get('amount'),
                'error_message' :  err_msg,
                'payment_status': post.get('STATUS')
            }
            payfort_error_capture_obj.sudo().create(payfort_error_capture_data)
            return request.render("bista_capturing_online_payment.payfort_payment_error_templet", {
                'payment_id':post.get('PAYID'),
                'order_id':post.get('orderID'),
                'err_msg':err_msg,
            })

        # create payfort payment captare
        payfort_capture_obj = env['payfort.payment.capture']
        paid_amount = self.get_orignal_amount(float(post.get('amount')))
        bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
            self.calculate_payfort_charges_value(paid_amount)
        payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('PAYID')),
                                                          ('reference_number','=',post.get('orderID'))],limit=1)
        reg_ids = env['registration'].sudo().search([('enquiry_no', '=', post['orderID'])])
        invoice_ids = env['account.invoice'].sudo().search([('number', '=', post['orderID'])],limit=1)
        voucher_rec = env['account.voucher'].sudo().search(
            [('payfort_type', '=', True), ('payfort_link_order_id', '=', post['orderID'])],limit=1)
        next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['orderID'])])
        re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('code','=',post['orderID'])]
                                                                                          , limit=1)
        tc_student_rec = env['trensfer.certificate'].sudo().search([('code', '=', post['orderID'])],limit=1)
        partner = False
        if len(reg_ids) > 0:
            partner = False
        elif len(invoice_ids) > 0:
            partner = invoice_ids.partner_id.id
        elif len(voucher_rec) > 0:
            partner = voucher_rec.partner_id.id
        elif len(next_year_advance_fee_rec) > 0:
            partner = next_year_advance_fee_rec.partner_id.id
        elif len(re_registration_parent_rec) > 0:
            partner = re_registration_parent_rec.name.id
        elif len(tc_student_rec) > 0:
            partner = tc_student_rec.name.id
        if not payfort_capture_rec.id:
            payfort_capture_data = {
                'date' : date.today(),
                'partner':partner,
                'pay_id' : post.get('PAYID') or '',
                'reference_number' :  post.get('orderID'),
                'paid_amount' : paid_amount,
                'bank_charges' : bank_charges,
                'gross_transaction_value' : gross_transaction_value,
                'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                'transaction_charges' : transaction_charges,
                'net_amount' : net_amount,
            }
            payfort_capture_obj.sudo().create(payfort_capture_data)
        return res