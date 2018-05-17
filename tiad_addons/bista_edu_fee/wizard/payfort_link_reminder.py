from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import hashlib
import time
from datetime import date

class ResendPayfortLink(models.Model):

    _name='resend.payfort.wiz'

    class_id = fields.Many2one('course', "Class")
    section_id = fields.Many2one('section', 'Section')
    parent_ids = fields.Many2many('res.partner','resend_payfort','payfort_id','parent_id','Parent')

    @api.model
    def _get_period(self):
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].find()
        return periods and periods[0] or False

    @api.model
    def _make_journal_search(self,ttype):
        journal_pool = self.env['account.journal']
        return journal_pool.search([('type', '=', ttype)])

    @api.model
    def _get_journal(self):
        if self._context is None: self._context = {}
        invoice_pool = self.env['account.invoice']
        journal_pool = self.env['account.journal']
        if self._context.get('invoice_id', False):
            invoice = invoice_pool.browse(self._context['invoice_id'])
            journal_id = journal_pool.search([('currency', '=', invoice.currency_id.id),
                                              ('company_id', '=', invoice.company_id.id)],
                                             limit=1)
            return journal_id and journal_id[0] or False
        if self._context.get('journal_id', False):
            return self._context.get('journal_id')
        if not self._context.get('journal_id', False) and self._context.get('search_default_journal_id', False):
            return self._context.get('search_default_journal_id')

        ttype = self._context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(ttype)
        return res and res[0] or False

    @api.model
    def _get_currency(self):
        if self._context is None: self._context = {}
        journal_pool = self.env['account.journal']
        journal_id = self._context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return self.env['res.users'].browse(self._uid).company_id.currency_id.id

    @api.model
    def resend_mail_for_payfort_payment(self,parent,total_amount,order_id,table_date):
        active_payforts=self.env['payfort.config'].search([('active','=','True')])
        if not active_payforts:
            raise except_orm(_('Warning!'),
            _("Please create Payfort Details First!") )

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
            _("There should be only one payfort record!"))
        charge = 0.0
        if active_payforts.id:
            charge=active_payforts.charge
            f_amount=((charge/100)*total_amount)+total_amount
            final_amount = str(int(round((f_amount + active_payforts.transaction_charg_amount),2) * 100))
            m = hashlib.sha1()
            if not active_payforts.sha_in_key:
                raise except_orm(_('Warning!'),
                            _("payfort SHA key not define!"))
            else:
                SHA_Key = active_payforts.sha_in_key
                PSP_ID =active_payforts.psp_id
                string_input='AMOUNT=%s' % (final_amount) + SHA_Key + 'CURRENCY=AED' + SHA_Key + 'LANGUAGE=EN_US' + SHA_Key + 'ORDERID=%s' % (order_id) + SHA_Key +'PSPID=%s'%(PSP_ID)+ SHA_Key
                ss='AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s'%(final_amount,order_id,PSP_ID)
                m.update(string_input)
                hashkey=m.hexdigest()
                hashkey=hashkey.upper()
                mail_obj=self.env['mail.mail']
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])
                link= str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss,hashkey,)
                mail_data={
                        'email_from':email_sender.smtp_user,
                        'email_to':parent.parents_email,
                        'subject':'Academic Fee Payment Reminder',
                        'body_html':'<div><p>Dear, %s </p> </br>'
                        '<p>This is gentle reminder for payments of all due fees for your child(ren).'
                        ' Please note that, as of today, the total outstanding payment is AED %s.'
                        'The details of invoices are in the table below.</p>'
                        '<br/><table border=%s><tr><td><b>Child Name</b></td><td><b>Invoice number</b></td>'
                        '<td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b>'
                        '</td></tr>%s</table>'
                        '<p>You can pay this fees online via the fee payment link below or visit the school'
                        ' fee counter to pay via cash or cheque. Online payments via Payfort includes convenience'
                        ' fees charged by the online service provider (Payfort) and the link will display'
                        ' the total value payable. Once paid by you,'
                        ' the receipt for the payment will be emailed to you as confirmation.</p><br/>'
                        '<a href=%s><button>Click Here to pay Fee</button></a><br/>'
                        "<p>Please contact the school's accounts team via accounts.tiadxb@iqraeducation.net if you need any clarifications.</p>"
                        '<p>Best Regards<br/>'
                        ' <br/>Registrar,'
                        ' <br/>The Indian Academy, Dubai'
                        ' <br/>http://www.indianacademydubai.com'
                        ' <br/>Phone : +971 04 2646746, +971 04 2646733, Toll Free: 800 INDIAN (463426)'
                        '<br/>Fax : +971 4 2644501'%(parent.name,total_amount,2,table_date,link)
                    }
            mail_id = mail_obj.create(mail_data)
            mail_obj.send(mail_id)

    @api.multi
    def resend_payfort_link(self):
        account_voucher_obj = self.env['account.voucher']
        account_invoice_obj = self.env['account.invoice']
        voucher_line_obj = self.env['account.voucher.line']
        if self.parent_ids:
            table_data = ''
            for parent_rec in self.parent_ids:
                student_id_list = []
                if self.class_id and self.section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id and self.section_id.id == child_rec.section_id.id:
                            student_id_list.append(child_rec.id)
                elif self.class_id and not self.section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id:
                            student_id_list.append(child_rec.id)
                    # stud_rec = parent_rec.chield1_ids.search([('class_id','=',self.class_id.id)])
                elif not self.class_id and self.section_id:
                    # stud_rec = parent_rec.chield1_ids.search([('section_id','=',self.section_id.id)])
                    for child_rec in parent_rec.chield1_ids:
                        if self.section_id.id == child_rec.section_id.id:
                            student_id_list.append(child_rec.id)
                else:
                    # stud_rec = parent_rec.chield1_ids
                    for child_rec in parent_rec.chield1_ids:
                        student_id_list.append(child_rec.id)
                stud_rec = self.env['res.partner'].browse(student_id_list)
                if len(stud_rec) > 0:
                    total_amount = 0.00
                    advance_paid_amount = 0.00
                    move_ids_list = []
                    stud_lst_invoice = []
                    for student_rec in stud_rec:
                        # if not student_rec.property_account_customer_advance:
                        #     raise except_orm(_("Warning!"), _('Please define Advance Account for student %s') % student_rec.name)
                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id)]):
                            if student_rec.id not in stud_lst_invoice:
                                stud_lst_invoice.append(student_rec.id)
                            if invoice_rec.payment_ids:
                                for payment_rec in invoice_rec.payment_ids:
                                    for move_rec in payment_rec.move_id:
                                        if move_rec.id not in move_ids_list:
                                            move_ids_list.append(move_rec.id)
                                            for move_line_rec in move_rec.line_id:
                                                if student_rec.property_account_customer_advance.id:
                                                    if move_line_rec.account_id.id == student_rec.property_account_customer_advance.id:
                                                        advance_paid_amount += move_line_rec.credit
                                                        advance_paid_amount -= move_line_rec.debit

                            if invoice_rec.state == 'open':
                                total_amount += invoice_rec.residual
                                table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(student_rec.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)
                    if total_amount >= advance_paid_amount:
                        total_amount -= advance_paid_amount
                    period_rec = self._get_period()
                    journal_rec = self._get_journal()
                    curency_id = self._get_currency()
                    vouch_sequence = self.env['ir.sequence'].get('voucher.payfort') or '/'
                    if total_amount > 0.00:
                        voucher_data = {
                            'period_id': period_rec.id,
                            'journal_id': journal_rec.id,
                            'account_id': journal_rec.default_debit_account_id.id,
                            'partner_id': parent_rec.id,
                            'currency_id': curency_id,
                            'reference': parent_rec.name,
                            'amount': 0.0,
                            'type': 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'payfort_type': True,
                            'payfort_link_order_id' : vouch_sequence,
                            # 'student_class' : self.class_id.id,
                            # 'student_section' : self.section_id.id,
                            }
                        voucher_rec = account_voucher_obj.create(voucher_data)

                        # c_date = date.today()
                        # for stud_id in stud_lst_invoice:
                        #     res = voucher_rec.onchange_partner_id(stud_id, 12, float(0.00), voucher_rec.currency_id.id,
                        #               voucher_rec.type, c_date)
                        #
                        #     for line_data in res['value']['line_cr_ids']:
                        #         voucher_lines = {
                        #             'move_line_id': line_data['move_line_id'],
                        #             'name': line_data['name'],
                        #             'amount_unreconciled': line_data['amount_unreconciled'],
                        #             'type': line_data['type'],
                        #             'amount_original': line_data['amount_original'],
                        #             'account_id': line_data['account_id'],
                        #             'voucher_id': voucher_rec.id,
                        #             'reconcile': True
                        #         }
                        #         asd = voucher_line_obj.sudo().create(voucher_lines)
                        #         print "asdasd",asd
                        #     print "======================"
                        #
                        # res = voucher_rec.onchange_partner_id(voucher_rec.partner_id.id, 12, 0.00, voucher_rec.currency_id,
                        #                                 voucher_rec.type, c_date)
                        #
                        # if res:
                        #     for line_data in res['value']['line_dr_ids']:
                        #         voucher_lines = {
                        #             'move_line_id': line_data['move_line_id'],
                        #             'amount': line_data['amount_original'] or line_data['amount'],
                        #             'name': line_data['name'],
                        #             'amount_unreconciled': line_data['amount_unreconciled'],
                        #             'type': line_data['type'],
                        #             'amount_original': line_data['amount_original'],
                        #             'account_id': line_data['account_id'],
                        #             'voucher_id': voucher_rec.id,
                        #         }
                        #
                        #         voucher_line_obj.sudo().create(voucher_lines)

                        # send mail for pay fort
                        self.resend_mail_for_payfort_payment(parent=parent_rec,total_amount=total_amount,order_id=vouch_sequence,table_date=table_data)