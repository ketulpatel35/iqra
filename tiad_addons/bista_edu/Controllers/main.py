from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp import http
from openerp.http import request,db_filter
import time
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning

class payfort_payment_status(http.Controller):

    # def _get_journal_with_currency_with_tax(self, inv):
    #     env = request.env(user=SUPERUSER_ID)
    #     journal_proxy = env['account.journal']
    #     journal = journal_proxy.search \
    #         ([('type', '=', 'bank'), ('company_id', '=', inv.company_id.id)],limit=1)
    #     if not journal:
    #         raise except_orm(_('Error!'),
    #                          _("No bank journal define for company %s") % (
    #                          inv.company_id.name,))
    #     tax_id = self._get_tax(journal.id)
    #     return inv.journal_id.id, inv.currency_id.id, tax_id
    #
    # def _get_tax(self,journal_id):
    #     env = request.env(user=SUPERUSER_ID)
    #     journal_pool = env['account.journal']
    #     journal = journal_pool.browse(journal_id)
    #     account_id = journal.default_credit_account_id or \
    #                  journal.default_debit_account_id
    #     if account_id and account_id.tax_ids:
    #         tax_id = account_id.tax_ids[0].id
    #         return tax_id
    #     return False

    def _get_period(self):
        env = request.env(user=SUPERUSER_ID)
        context = env.context
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = env['account.period'].find(context=ctx)
        return periods and periods[0] or False

    # def get_value_vouchar(self,inv_id):
    #     env = request.env(user=SUPERUSER_ID)
    #     inv_obj = env['account.invoice']
    #     journal_obj = env['account.journal']
    #     vou_obj = env['account.voucher']
    #     inv = inv_obj.browse(inv_id)
    #     journal_id, currency_id, tax_id = \
    #         self._get_journal_with_currency_with_tax(inv)
    #     amount = inv.type in (
    #     'out_refund', 'in_refund') and -inv.residual or inv.residual
    #     date = time.strftime('%Y-%m-%d')
    #     partner_id = env['res.partner']._find_accounting_partner(
    #         inv.partner_id).id
    #     cash_journal = journal_obj.search([('type', '=', 'bank')],limit=1)
    #     values = vou_obj.onchange_journal(cash_journal.id, [],False, partner_id, date, amount,'receipt', inv.company_id.id,)
    #     return {
    #         'active': True,
    #         'period_id': inv.period_id.id,
    #         'partner_id': partner_id,
    #         'journal_id': 12,
    #         'reference': inv.name,
    #         'amount': amount,
    #         'default_type': 'payment',
    #         'invoice_id': inv.id,
    #         'currency_id': inv.currency_id and inv.currency_id.id or False,
    #         'close_after_process': True,
    #         'type': inv.type in (
    #         'out_invoice', 'out_refund') and 'receipt' or 'payment',
    #         'state': 'draft',
    #         'pay_now': 'pay_now',
    #         'pre_line': values['value'].get('pre_line', False),
    #         'c_line_dr_ids': values['value'].get('line_dr_ids', []),
    #         'c_line_cr_ids': values['value'].get('line_cr_ids', []),
    #         'date': date,
    #         'tax_id': tax_id,
    #         'payment_option': 'without_writeoff',
    #         'comment': _('Write-Off'),
    #         'payment_rate': values['value'].get('payment_rate', 1.0),
    #         'payment_rate_currency_id': values['value'].get(
    #             'payment_rate_currency_id', currency_id) or False,
    #         'account_id': inv.account_id.id or values['value'].get(
    #             'account_id', False) or False,
    #         'name': values['value'].get('name', inv.name)
    #     }

    def _get_currency(self):
        """
        this method use for get account currency.
        --------------------------------------------
        :return: record set of  currency.
        """
        env = request.env(user=SUPERUSER_ID)
        # if self._context is None: self._context = {}
        journal_pool = env['account.journal']
        journal_id = env.context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return env['res.users'].browse(env.uid).company_id.currency_id.id

    def next_year_advance_payment(self,env,next_year_advance_fee_rec,order_id,amount,pay_id):
        """
        This method use to online payment for next acdemic year in Advance.
        --------------------------------------------------------------------
        :param env: SUPERUSER object
        :param next_year_advance_fee_rec: record set of next year adv payment object
        :param order_id: unique order id
        :param amount: advance payment amount
        :return:
        """
        voucher_obj = env['account.voucher']
        partner_id = next_year_advance_fee_rec.partner_id.id
	t_date = date.today()
        period_id = self._get_period().id
        account_id = env['account.journal'].browse(12).default_debit_account_id.id
        total_amount = self.get_orignal_amount(amount)
        print "TOTAL AMOUNT : -->",total_amount
        currency_id = self._get_currency()
        voucher_data = {
                'period_id': period_id,
                'account_id': account_id,
                'partner_id': partner_id,
                'journal_id': 12,
                'currency_id': currency_id,
                'reference': order_id,
                'amount': total_amount,
                'type': 'receipt' or 'payment',
                'state': 'draft',
                'pay_now': 'pay_later',
                'name': '',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': 1,
                'tax_id': False,
                'payment_option': 'without_writeoff',
                'comment': _('Write-Off'),
		'payfort_payment_id' : pay_id,
		'payfort_pay_date' : t_date,
            }

        voucher_id = voucher_obj.sudo().create(voucher_data)

        # Add Journal Entries with Advance Acc.
        voucher_id.button_proforma_voucher()

        next_year_advance_fee_rec.total_paid_amount += total_amount
        if next_year_advance_fee_rec.total_amount <= next_year_advance_fee_rec.total_paid_amount:
            next_year_advance_fee_rec.state = 'fee_paid'
            next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_pay'
	    next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
	    next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
        elif next_year_advance_fee_rec.total_paid_amount < next_year_advance_fee_rec.total_amount and next_year_advance_fee_rec.total_paid_amount != 0.00:
            next_year_advance_fee_rec.state = 'fee_partial_paid'
            next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_partial_pay'
	    next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
	    next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
        next_year_advance_fee_rec.payment_ids = [(4,voucher_id.id)]
        next_year_advance_fee_rec.journal_ids = [(4,12)]
        next_year_advance_fee_rec.journal_id = 12

        # send mail to perent with fee recipt
        email_server = env['ir.mail_server']
        email_sender = email_server.sudo().search([])
        ir_model_data = env['ir.model.data']
        template_id = ir_model_data.get_object_reference('bista_edu','email_template_academic_fee_receipt_paid')[1]
        template_rec = env['email.template'].sudo().browse(template_id)
        template_rec.sudo().write(
        {'email_to': next_year_advance_fee_rec.partner_id.parents1_id.parents_email, 'email_from': email_sender.smtp_user})
        template_rec.send_mail(voucher_id.id, force_send=False)

    def get_orignal_amount(self,amount):
        """
        this method use to convert orignal amount
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')])
        amount = float(amount)
        if len(active_payforts_rec) == 1:
            # divide by 100
            # amount /= 100.00
            # remove Transport charge
            if active_payforts_rec.transaction_charg_amount != 0:
                transaction_charg_amount = active_payforts_rec.transaction_charg_amount
            else:
                transaction_charg_amount = 0.50
            amount -= transaction_charg_amount
            # removed payfort charge amount
            if active_payforts_rec.charge != 0:
                act_amount=(amount*100)/(100+active_payforts_rec.charge)
            else:
                act_amount=(amount*100)/(100+2.10)

            return round(act_amount, 2)
        else:
            # amount /= 100
            amount -= 0.50
            act_amount=(amount*100)/(100+2.10)
            return act_amount

    def resend_academic_fee_payment(self, voucher_rec, amount, env, pay_id):
        """
        This method use when fee payment from resend payfort
        link, pay from parent.
        hear, already create voucher with 0.00 amount of parent.
        ------------------------------------------------------------
        :param voucher_rec: parent voucher record set with 0.00 amount
        :param amount: amount to pay from parent
        :param env: environment object
        :param payment_id: unique payment id genaret from payfort payment,
        :return:
        """
        voucher_line_obj = env['account.voucher.line']
        date = time.strftime('%Y-%m-%d')
        # assign payble amount to voucher
        if len(voucher_rec) == 1 and amount != 0:
            amount = float(amount)
            update_amount = self.get_orignal_amount(amount)
            voucher_rec.amount = update_amount
        for voucher in voucher_rec:
	    voucher.write({'payfort_payment_id' : pay_id, 'journal_id' : 12})
            res = voucher.onchange_partner_id(voucher.partner_id.id, 12, float(amount), voucher.currency_id.id,
                                              voucher.type, date)
            for line_data in res['value']['line_cr_ids']:
                voucher_lines = {
                    'move_line_id': line_data['move_line_id'],
                    'amount': line_data['amount_original'] or line_data['amount'],
                    'name': line_data['name'],
                    'amount_unreconciled': line_data['amount_unreconciled'],
                    'type': line_data['type'],
                    'amount_original': line_data['amount_original'],
                    'account_id': line_data['account_id'],
                    'voucher_id': voucher.id,
                    'reconcile': True
                }
                voucher_line_obj.sudo().create(voucher_lines)

            for line_data in res['value']['line_dr_ids']:
                voucher_lines = {
                    'move_line_id': line_data['move_line_id'],
                    'amount': float(amount),
                    'name': line_data['name'],
                    'amount_unreconciled': line_data['amount_unreconciled'],
                    'type': line_data['type'],
                    'amount_original': line_data['amount_original'],
                    'account_id': line_data['account_id'],
                    'voucher_id': voucher.id,
                }

                voucher_line_obj.sudo().create(voucher_lines)

            # Validate voucher (Add Journal Entries)
            voucher.button_proforma_voucher()

            # send mail to perent with fee recipt
            email_server = env['ir.mail_server']
            email_sender = email_server.sudo().search([])
            ir_model_data = env['ir.model.data']
            template_id = ir_model_data.get_object_reference('bista_edu','email_template_academic_fee_receipt_paid')[1]
            template_rec = env['email.template'].sudo().browse(template_id)
            template_rec.sudo().write(
            {'email_to': voucher.partner_id.parents_email, 'email_from': email_sender.smtp_user})
            template_rec.send_mail(voucher.id, force_send=False)

    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use When Online Payment using Payfot getway.
        ----------------------------------------------------------
        :param post:
        :return:it redirect thankyou page if transactions success
                otherwise redirect to transactions fail page.
        """
        env = request.env(user=SUPERUSER_ID)
        voucher_pool = env['account.voucher']
        voucher_line_pool = env['account.voucher.line']
        reg_ids = env['registration'].sudo().search([('enquiry_no', '=', post['orderID'])])
        invoice_ids = env['account.invoice'].sudo().search([('number', '=', post['orderID'])])
        voucher_rec = env['account.voucher'].sudo().search(
            [('payfort_type', '=', True), ('payfort_link_order_id', '=', post['orderID'])])
        next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['orderID'])])

        if len(reg_ids) > 0:
            pay_id = ''
            if post['STATUS'] == '9':
                for each in reg_ids:
                    each.fee_status = 'reg_fee_pay'
                    each.pay_id = post['PAYID']
                    datestring = post['TRXDATE']
                    datestring = datestring[:6] + '20' + datestring[6:]
                    c = time.strptime(datestring, "%m/%d/%Y")
                    c1 = time.strftime("%Y-%m-%d", c)
                    each.trx_date = c1
                    pay_id = each.pay_id
                    jounral_dict1 = {}
                    jounral_dict2 = {}
                    account_move_obj = env['account.move']
                    exist_stu_fee = account_move_obj.sudo().search_count([('ref', '=', each.enquiry_no)])
                    # journal_id = env['account.journal'].search([('name','=','Online Payment'),('type','=','bank')],limit=1)
                    # if journal_id.id:

                    account_move_obj = env['account.move']
                    account_id = env['account.account'].search([('code', '=', '402050')], limit=1)

                    if exist_stu_fee == 0:
                        for student_fee_rec in each.reg_fee_line:
                            if student_fee_rec.amount:
                                jounral_dict1.update({'name': each.name, 'debit': student_fee_rec.amount})
                                jounral_dict2.update(
                                    {'name': each.name, 'credit': student_fee_rec.amount, 'account_id': account_id.id})
                        move_id = account_move_obj.sudo().create(
                            {'journal_id': 12, 'line_id': [(0, 0, jounral_dict1), (0, 0, jounral_dict2)],
                             'ref': each.enquiry_no})
                        each.reg_fee_receipt = move_id.id

                    # code for sending fee receipt to student
                    mail_obj = env['mail.mail']
                    email_server = env['ir.mail_server']
                    email_sender = email_server.sudo().search([])
                    ir_model_data = env['ir.model.data']
                    template_id = \
                    ir_model_data.get_object_reference('bista_edu', 'email_template_registration_receipt')[1]
                    template_rec = env['email.template'].sudo().browse(template_id)
                    template_rec.sudo().write({'email_to': each.email, 'email_from': email_sender.smtp_user})
                    template_rec.send_mail(each.id, force_send=True)
                    return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
                        'pay_id': pay_id})
            else:
                return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
                })

        if len(invoice_ids) > 0:
            if post['STATUS'] == '9':
                datestring = post['TRXDATE']
                # amount = float(post['amount'])
                datestring = datestring[:6] + '20' + datestring[6:]
                c = time.strptime(datestring, "%m/%d/%Y")
                tran_date = time.strftime("%Y-%m-%d", c)
                reg_obj = env['registration']
                inv_id = ""
                for inv_obj in invoice_ids:
                    if inv_obj.state == 'open':
                        amount = inv_obj.residual
                        journal_id = env['account.journal'].browse(12)
                        voucher_data = {
                            'period_id': inv_obj.period_id.id,
                            'account_id': journal_id.default_debit_account_id.id,

                            'partner_id': inv_obj.partner_id.id,
                            'journal_id': journal_id.id,
                            'currency_id': inv_obj.currency_id.id,
                            'reference': inv_obj.name,  # payplan.name +':'+salesname
                            # 'narration': data[0]['narration'],
                            'amount': amount,
                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
			    'payfort_payment_id' : post['PAYID'],
			    'payfort_pay_date' : tran_date,
                        }

                        voucher_id = voucher_pool.sudo().create(voucher_data)
                        date = time.strftime('%Y-%m-%d')
                        if voucher_id:
                            res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, 12, inv_obj.amount_total,
                                                                 inv_obj.currency_id.id, inv_obj.type, date)
                            # Loop through each document and Pay only selected documents and create a single receipt
                            for line_data in res['value']['line_cr_ids']:
                                if not line_data['amount']:
                                    continue
                                name = line_data['name']

                                if line_data['name'] in [inv_obj.number]:
                                    if not line_data['amount']:
                                        continue
                                    voucher_lines = {
                                        'move_line_id': line_data['move_line_id'],
                                        'amount': amount,
                                        'name': line_data['name'],
                                        'amount_unreconciled': line_data['amount_unreconciled'],
                                        'type': line_data['type'],
                                        'amount_original': line_data['amount_original'],
                                        'account_id': line_data['account_id'],
                                        'voucher_id': voucher_id.id,
                                        'reconcile': True
                                    }
                                    voucher_line_pool.sudo().create(voucher_lines)

                            for line_data in res['value']['line_dr_ids']:

                                if not line_data['amount']:
                                    continue

                                if line_data['name'] in [inv_obj.number]:
                                    if not line_data['amount']:
                                        continue
                                    voucher_lines = {
                                        'move_line_id': line_data['move_line_id'],
                                        'amount': amount,
                                        'name': line_data['name'],
                                        'amount_unreconciled': line_data['amount_unreconciled'],
                                        'type': line_data['type'],
                                        'amount_original': line_data['amount_original'],

                                        'account_id': line_data['account_id'],
                                        'voucher_id': voucher_id.id,
                                    }
                                    voucher_line_id = voucher_line_pool.sudo().create(voucher_lines)

                            # Add Journal Entries
                            voucher_id.button_proforma_voucher()
                            # payment date and payment id store in invoice
                            inv_obj.payfort_pay_date = tran_date
                            inv_obj.payfort_payment_id = post['PAYID']

                            partner_id = inv_obj.partner_id
                            reg_ids = reg_obj.sudo().search([('student_id', '=', partner_id.id)])

                            # code for sending fee receipt to student
                            if len(reg_ids) > 0:
                                for each in reg_ids:
                                    each.fee_status = 'academy_fee_pay'
                                    each.acd_pay_id = post['PAYID']
                                    each.acd_trx_date = tran_date
                                    email_server = env['ir.mail_server']
                                    email_sender = email_server.sudo().search([])
                                    ir_model_data = env['ir.model.data']
                                    template_id = ir_model_data.get_object_reference('bista_edu',
                                                                                     'email_template_academic_fee_receipt_paid')[
                                        1]
                                    template_rec = env['email.template'].sudo().browse(template_id)
                                    template_rec.sudo().write(
                                        {'email_to': each.email, 'email_from': email_sender.smtp_user})
                                    template_rec.send_mail(voucher_id.id, force_send=True)

                                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                        'pay_id': post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                })

        if len(voucher_rec) > 0:
            if post['STATUS']=='9':
                self.resend_academic_fee_payment(voucher_rec=voucher_rec,
                                                 amount=post.get('amount'),
                                                 env=env,
						 pay_id = post['PAYID'])
                return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                'pay_id': post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                      })

        if len(next_year_advance_fee_rec) > 0:
            if post['STATUS']=='9':
                order_id = post['orderID']
                c_amount = post['amount']
		payment_id = post['PAYID']
                self.next_year_advance_payment(env=env,
                                               next_year_advance_fee_rec=next_year_advance_fee_rec,
                                               order_id=order_id,
                                               amount=c_amount,
						pay_id = payment_id)

                return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                    'pay_id':post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
