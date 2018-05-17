from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import hashlib
import time
from datetime import date

class ResendPayfortLink(models.Model):

    _name='resend.payfort.wiz'

    class_id = fields.Many2one('course', "Class")
    student_section_id = fields.Many2one('section', 'Section')
    parent_ids = fields.Many2many('res.partner','resend_payfort','payfort_id','parent_id','Parent')

    @api.onchange('class_id')
    def onchange_class_id(self):
        res = {}
        parent_list = []
        if self.class_id.id:
           for student_record in self.env['res.partner'].search([('is_parent','=',False),('is_student','=',True)]):
               if student_record.course_id.id == self.class_id.id:
                   if student_record.parents1_id.id not in parent_list:
                       parent_list.append(student_record.parents1_id.id)
        else:
            for parent_rec in self.env['res.partner'].search([('is_parent','=',True),('is_student','=',False)]):
                parent_list.append(parent_rec.id)
        res.update({'parent_ids':[('is_parent','=',True),('is_student','=',False),('id','in',parent_list)]})
        return {'domain':res}

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
    def resend_mail_for_payfort_payment_old_9august2016(self,parent,total_amount,order_id,table_date,advance_table,\
                                        voucher,advance_amt,invoice_amt):
                                        
        active_payforts=self.env['payfort.config'].search([('active','=','True')])
        if not active_payforts:
            raise except_orm(_('Warning!'),
            _("Please create Payfort Details First!") )

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
            _("There should be only one payfort record!"))
        charge = 0.0
        payable_amount = total_amount
        if active_payforts.id:
            if active_payforts.charge != 0.00:
                total_amount += (total_amount * active_payforts.charge) / 100
            if active_payforts.transaction_charg_amount > 0.00:
                total_amount += active_payforts.transaction_charg_amount
            payfort_amount = round(total_amount,2)
            final_amount = str(int(payfort_amount * 100))

            #PARENTS ADVANCE AMOUNT
            advance_amt += parent.advance_total_recivable + parent.re_reg_total_recivable
            parent_total_recivable = 0.0
            if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
                parent_total_recivable = 0.0
            elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
                parent_total_recivable = parent.advance_total_recivable  + parent.re_reg_total_recivable

             
            m = hashlib.sha1()
            if not active_payforts.sha_in_key:
                raise except_orm(_('Warning!'),
                            _("payfort SHA key not define!"))
            else:
                SHA_Key = active_payforts.sha_in_key
                PSP_ID = active_payforts.psp_id
                string_input='AMOUNT=%s' % (final_amount) + SHA_Key + 'CURRENCY=AED' + SHA_Key + 'LANGUAGE=EN_US' + SHA_Key + 'ORDERID=%s' % (order_id) + SHA_Key +'PSPID=%s'%(PSP_ID)+ SHA_Key
                ss='AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s'%(final_amount,order_id,PSP_ID)
                m.update(string_input)
                hashkey=m.hexdigest()
                hashkey=hashkey.upper()

                link= str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss,hashkey,)

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('bista_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
                template_rec = self.env['email.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
                body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
                body_dynamic_html += 'Total advances (if any):<br/>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
                body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
                body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
                body_dynamic_html += '<p>Total outstanding payment is AED %s.</p></div>'%(payable_amount)
                body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                template_rec.write({'email_from': email_sender.smtp_user,
                                    'email_to': parent.parents_email,
                                    'email_cc': 'Erpemails_ais@iqraeducation.net',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(voucher.id)
                template_rec.body_html = body_html

    @api.model
    def resend_mail_for_payfort_payment(self,parent,total_amount,order_id,table_date,advance_table,\
                                        voucher,advance_amt,invoice_amt):
                                        
        active_payforts=self.env['payfort.config'].search([('active','=','True')])
        if not active_payforts:
            raise except_orm(_('Warning!'),
            _("Please create Payfort Details First!") )

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
            _("There should be only one payfort record!"))
        charge = 0.0
        payable_amount = total_amount
        if active_payforts.id:
            if active_payforts.charge != 0.00:
                total_amount += (total_amount * active_payforts.charge) / 100
            if active_payforts.transaction_charg_amount > 0.00:
                total_amount += active_payforts.transaction_charg_amount
            payfort_amount = round(total_amount,2)
            final_amount = str(int(payfort_amount * 100))

            #PARENTS ADVANCE AMOUNT
            advance_amt += parent.advance_total_recivable + parent.re_reg_total_recivable
            parent_total_recivable = 0.0
            if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
                parent_total_recivable = 0.0
            elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
                parent_total_recivable = parent.advance_total_recivable  + parent.re_reg_total_recivable

             
            m = hashlib.sha1()
            if not active_payforts.sha_in_key:
                raise except_orm(_('Warning!'),
                            _("payfort SHA key not define!"))
            else:
                SHA_Key = active_payforts.sha_in_key
                PSP_ID = active_payforts.psp_id
                string_input='AMOUNT=%s' % (final_amount) + SHA_Key + 'CURRENCY=AED' + SHA_Key + 'LANGUAGE=EN_US' + SHA_Key + 'ORDERID=%s' % (order_id) + SHA_Key +'PSPID=%s'%(PSP_ID)+ SHA_Key
                ss='AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s'%(final_amount,order_id,PSP_ID)
                m.update(string_input)
                hashkey=m.hexdigest()
                hashkey=hashkey.upper()

                link= str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss,hashkey,)

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('bista_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
                template_rec = self.env['email.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
                body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
                body_dynamic_html += 'Total advances (if any):<br/>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
                body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
                body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
                body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                template_rec.write({'email_from': email_sender.smtp_user,
                                    'email_to': parent.parents_email,
                                    'email_cc': 'Erpemails_ais@iqraeducation.net',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(voucher.id)
                template_rec.body_html = body_html

    @api.multi
    def resend_payfort_link(self):
        account_voucher_obj = self.env['account.voucher']
        account_invoice_obj = self.env['account.invoice']
        voucher_line_obj = self.env['account.voucher.line']
                                        
        if self.parent_ids:
            for parent_rec in self.parent_ids:
                table_data = ''
                student_id_list = []
                stud_advance_table = ''
                total_advance = 0.0
                parent_cedit = 0.00
                if self.class_id and self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id and self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                elif self.class_id and not self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                    # stud_rec = parent_rec.chield1_ids.search([('class_id','=',self.class_id.id)])
                elif not self.class_id and self.student_section_id:
                    # stud_rec = parent_rec.chield1_ids.search([('student_section_id','=',self.student_section_id.id)])
                    for child_rec in parent_rec.chield1_ids:
                        if self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                else:
                    # stud_rec = parent_rec.chield1_ids
                    for child_rec in parent_rec.chield1_ids:
                        if child_rec.active != False:
                            student_id_list.append(child_rec.id)
                stud_rec = self.env['res.partner'].browse(student_id_list)
                if len(stud_rec) > 0:
                    # check for parent advance payment#this is my logic
                    if parent_rec.credit :
                        parent_cedit += parent_rec.credit

                    total_amount_table = 0.00
                    total_amount =0.0
                    move_ids_list = []
                    stud_lst_invoice = []
                    stud_balance=0.0
                    total_amount += parent_cedit                    

                    for student_rec in stud_rec:
                        
                        # COLLECT STUDENT ADVANCES
                        total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                        advance_total_recivable = 0.0
                        if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
                            advance_total_recivable = 0.0
                        elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
                            advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable

                        stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                        
                        
                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id)]):
                            #GET OPEN INVOICES
                            if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
                                total_amount_table += invoice_rec.residual
                                table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(student_rec.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)
#                                                     
                        total_amount += student_rec.credit

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
                            # 'student_section' : self.student_section_id.id,
                            }
                        voucher_rec = account_voucher_obj.create(voucher_data)

                        # SEND MAIL FOR PAY FORT
                        self.resend_mail_for_payfort_payment(parent=parent_rec,total_amount=total_amount,order_id=vouch_sequence,\
                            table_date=table_data,advance_table=stud_advance_table,\
                            voucher=voucher_rec,advance_amt=total_advance,invoice_amt=total_amount_table)


