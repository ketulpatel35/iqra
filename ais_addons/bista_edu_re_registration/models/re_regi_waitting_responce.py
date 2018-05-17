# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import netsvc
import openerp
import base64, re
import hashlib
import time

class ReRegistrationResponceParents(models.Model):
    _name = 're.reg.waiting.responce.parents'

    @api.depends('student_ids')
    def compute_payable_amount(self):
        for record in self:
            amount = 0.00
            for stud_rec in record.student_ids:
                amount += stud_rec.total_amount
            record.total_amount = amount

    @api.depends('student_ids')
    def compute_total_paid_amount(self):
        for record in self:
            paid_amount = 0.00
            for stud_rec in record.student_ids:
                paid_amount += stud_rec.total_paid_amount
            record.total_paid_amount = paid_amount

    @api.depends('total_amount', 'total_paid_amount')
    def compute_residual_amount_parent(self):
        for record in self:
            record.residual = record.total_amount - record.total_paid_amount

    code = fields.Char('Code')
    name = fields.Many2one('res.partner', 'Name')
    state = fields.Selection([('awaiting_response', 'Awaiting Response'),
                              ('awaiting_re_registration_fee', 'Awaiting Re-Registration Fee'), \
                              ('re_registration_confirmed', 'Re-Registration Confirmed')])
    student_ids = fields.One2many('re.reg.waiting.responce.student', 're_reg_parents', 'Reg Childs')
    parent_contact = fields.Char(related='name.parent_contact')
    total_amount = fields.Float('Total Amount', compute='compute_payable_amount')
    total_paid_amount = fields.Float('Total Paid Amount', compute='compute_total_paid_amount')
    residual = fields.Float('Balance', compute='compute_residual_amount_parent')
    request_batch_id = fields.Many2one("batch", "Next Academic Year")

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].get('re.reg.parent.form') or '/'
        res = super(ReRegistrationResponceParents, self).create(vals)
        return res

    @api.multi
    def button_re_ref_awaiting_fee(self):
        self.come_to_awaiting_fee()

    @api.multi
    def re_send_payfort_payment_link_parent(self):
        for parent_re_reg_rec in self:
            if parent_re_reg_rec.residual > 0.00:
                child_data_table = ''
                for student_re_record in parent_re_reg_rec.student_ids:
                    child_data_table += '<tr>'
                    child_data_table += '<td>%s</td>' % (student_re_record.name.name)
                    child_data_table += '<td>%s</td>' % (student_re_record.next_year_course_id.name)
                    child_data_table += '<td>Yes</td>'
                    child_data_table += '<td>%s</td>' % (student_re_record.total_amount)
                    child_data_table += '</tr>'
                self.send_re_registration_payment_link(parent_record=parent_re_reg_rec,
                                                       child_data_table=child_data_table)

    @api.model
    def send_re_registration_payment_link(self, parent_record, child_data_table):
        """
        this method is use to send mail to parent for pay
        re-registration fee.
        :param parent_record: re-registration parent record set
        :param amount: total payable amount
        :return:
        """
        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])

        if not active_payforts:
            raise except_orm(_('Warning!'),
                             _("Please create Payfort Details First!"))
        elif len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
                             _("There should be only one payfort record!"))
        elif not active_payforts.sha_in_key:
            raise except_orm(_('Warning!'),
                             _("payfort SHA key not define!"))
        elif not active_payforts.psp_id:
            raise except_orm(_('Warning!'),
                             _("payfort PSP ID not define!"))

        amount = parent_record.residual
        for student_re_rec in parent_record.student_ids:
            if student_re_rec.name.credit > 0.00:
                amount += student_re_rec.name.credit
        if active_payforts.id:
            if active_payforts.charge != 0.00:
                amount += (amount * active_payforts.charge) / 100
            if active_payforts.transaction_charg_amount > 0.00:
                amount += active_payforts.transaction_charg_amount
            payfort_amount = round(amount,2)
        final_amount = str(int(payfort_amount * 100))
        # charge = active_payforts.charge
        # with_charge_amount = ((charge / 100) * amount) + amount
        # final_amount = str(int(round((with_charge_amount + active_payforts.transaction_charg_amount), 2) * 100))
        SHA_Key = active_payforts.sha_in_key
        PSP_ID = active_payforts.psp_id
        order_id = parent_record.code
        string_input = 'AMOUNT=%s' % (
        final_amount) + SHA_Key + 'CURRENCY=AED' + SHA_Key + 'LANGUAGE=EN_US' + SHA_Key + 'ORDERID=%s' % (
        order_id) + SHA_Key + 'PSPID=%s' % (PSP_ID) + SHA_Key
        ss = 'AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s' % (final_amount, order_id, PSP_ID)
        m = hashlib.sha1()
        m.update(string_input)
        hashkey = m.hexdigest()
        hashkey = hashkey.upper()
        link = str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss, hashkey,)
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

    @api.model
    def _get_period(self):
        """
        this method use for get account period.
        ---------------------------------------
        :return: record set of period
        """
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].find()
        return periods and periods[0] or False

    @api.model
    def _make_journal_search(self, ttype):
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
        """
        this method use for get account currency.
        --------------------------------------------
        :return: record set of  currency.
        """
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

    @api.multi
    def create_attachment_payment_receipt(self, voucher, re_regi):
        attachment_obj = self.env['ir.attachment']
        result = False
        for record in voucher:
            ir_actions_report = self.env['ir.actions.report.xml']
            matching_report = ir_actions_report.search([('name', '=', 'Student Payment Receipt')])
            if matching_report:
                result, format = openerp.report.render_report(self._cr, self._uid, [record.id],
                                                              matching_report.report_name, {'model': 'account.voucher'})
                eval_context = {'time': time, 'object': record}
                if not matching_report.attachment or not eval(matching_report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = record.name_get()[0][1]
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                    file_name += ".pdf"
                    attachment_id = attachment_obj.create({
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': re_regi._name,
                        'res_id': re_regi.id,
                        'type': 'binary'
                    })

    @api.model
    def re_reg_fee_reconcile_stud_advance(self, re_reg_partner_rec, amount):
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        journal_rec = self._get_journal()
        account_id = journal_rec.default_debit_account_id.id
        partner_rec = re_reg_partner_rec.name
        currency_id = self._get_currency()
        period_id = self._get_period().id
        c_date = time.strftime('%Y-%m-%d')
        re_reg_advance_account = partner_rec.re_reg_advance_account or False
        if not re_reg_advance_account.id:
            raise except_orm(_('Warning!'),
                            _("Please define re-registration advance account!"))
        voucher_data = {
            'period_id': period_id,
            'account_id': account_id,
            'partner_id': partner_rec.id,
            'journal_id': journal_rec.id,
            'currency_id': currency_id,
            'reference': re_reg_partner_rec.code,
            'amount': 0.00,
            'type': 'receipt' or 'payment',
            'state': 'draft',
            'pay_now': 'pay_later',
            'name': re_reg_partner_rec.code,
            'date': c_date,
            'company_id': 1,
            'tax_id': False,
            'payment_option': 'without_writeoff',
            'comment': _('Write-Off'),
            'advance_account_id': re_reg_advance_account.id or False,
            're_reg_fee': True,
        }
        voucher_rec = voucher_obj.create(voucher_data)
        if voucher_rec.id:
            res = voucher_rec.onchange_partner_id(partner_rec.id, journal_rec.id, amount,
                                                  currency_id, voucher_rec.type, c_date)

            # Loop through each document and Pay only selected documents and create a single receipt
            # for line_data in res['value']['line_cr_ids']:
            #     voucher_lines = {
            #         'move_line_id': line_data['move_line_id'],
            #         'amount': line_data['amount_original'],
            #         'name': line_data['name'],
            #         'amount_unreconciled': line_data['amount_unreconciled'],
            #         'type': line_data['type'],
            #         'amount_original': line_data['amount_original'],
            #         'account_id': line_data['account_id'],
            #         'voucher_id': voucher_rec.id,
            #         'reconcile': True
            #     }
            #     voucher_line_obj.sudo().create(voucher_lines)

            for line_data in res['value']['line_dr_ids']:
                if amount > 0:
                    set_amount = line_data['amount_original']
                    if amount <= set_amount:
                        set_amount = amount
                    reconcile = False
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher_rec.id,
                    }
                voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
                reconsile_vals = voucher_line_rec.onchange_amount(line_data['amount_original'],set_amount)
                voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                if voucher_line_rec.reconcile:
                    amount_vals = voucher_line_rec.onchange_reconcile(voucher_line_rec.reconcile,line_data['amount_original'],set_amount)
                    voucher_line_rec.amount = amount_vals['value']['amount']
                else:
                    voucher_line_rec.amount = set_amount
                # a = 10 / 0
                amount -= set_amount
            # validate voucher
            voucher_rec.button_proforma_voucher()

    # @api.model
    # def re_reg_fee_reconcile_parent_advance(self, re_student_rec, amount, re_parent_rec):
    #     voucher_obj = self.env['account.voucher']
    #     voucher_line_obj = self.env['account.voucher.line']
    #     journal_rec = self._get_journal()
    #     account_id = journal_rec.default_debit_account_id.id
    #     partner_rec = re_student_rec.name
    #     currency_id = self._get_currency()
    #     period_id = self._get_period().id
    #     c_date = time.strftime('%Y-%m-%d')
    #     re_reg_advance_account = partner_rec.re_reg_advance_account or False
    #     if not re_reg_advance_account.id:
    #         raise except_orm(_('Warning!'),
    #                         _("Please define re-registration advance account!"))
    #     voucher_data = {
    #         'period_id': period_id,
    #         'account_id': account_id,
    #         'partner_id': partner_rec.id,
    #         'journal_id': journal_rec.id,
    #         'currency_id': currency_id,
    #         'reference': re_student_rec.code,
    #         'amount': 0.00,
    #         'type': 'receipt' or 'payment',
    #         'state': 'draft',
    #         'pay_now': 'pay_later',
    #         'name': re_student_rec.code,
    #         'date': c_date,
    #         'company_id': 1,
    #         'tax_id': False,
    #         'payment_option': 'without_writeoff',
    #         'comment': _('Write-Off'),
    #         'advance_account_id': re_reg_advance_account.id or False,
    #         're_reg_fee': True,
    #     }
    #     voucher_rec = voucher_obj.create(voucher_data)
    #     if voucher_rec.id:
    #         res = voucher_rec.onchange_partner_id(re_parent_rec.name.id, journal_rec.id, amount,
    #                                               currency_id, voucher_rec.type, c_date)
    #         # Loop through each document and Pay only selected documents and create a single receipt
    #         # for line_data in res['value']['line_cr_ids']:
    #         #     voucher_lines = {
    #         #         'move_line_id': line_data['move_line_id'],
    #         #         'amount': line_data['amount_original'],
    #         #         'name': line_data['name'],
    #         #         'amount_unreconciled': line_data['amount_unreconciled'],
    #         #         'type': line_data['type'],
    #         #         'amount_original': line_data['amount_original'],
    #         #         'account_id': line_data['account_id'],
    #         #         'voucher_id': voucher_rec.id,
    #         #         'reconcile': True
    #         #     }
    #         #     voucher_line_obj.sudo().create(voucher_lines)
    #
    #         for line_data in res['value']['line_dr_ids']:
    #             if amount > 0:
    #                 set_amount = line_data['amount_original']
    #                 if amount <= set_amount:
    #                     set_amount = amount
    #                 voucher_lines = {
    #                     'move_line_id': line_data['move_line_id'],
    #                     'amount': set_amount,
    #                     'name': line_data['name'],
    #                     'amount_unreconciled': line_data['amount_unreconciled'],
    #                     'type': line_data['type'],
    #                     'amount_original': line_data['amount_original'],
    #                     'account_id': line_data['account_id'],
    #                     'voucher_id': voucher_rec.id,
    #                 }
    #             amount -= set_amount
    #             voucher_line_obj.sudo().create(voucher_lines)
    #
    #             # validate voucher
    #             voucher_rec.button_proforma_voucher()

    @api.multi
    def come_to_awaiting_fee(self):
        fees_structure_obj = self.env['fees.structure']
        for parent_record in self:
            child_data_table = ''
            for student_record in parent_record.student_ids:
                child_data_table += '<tr>'
                child_data_table += '<td>%s</td>' % (student_record.name.name)
                child_data_table += '<td>%s</td>' % (student_record.next_year_course_id.name)
                student_record.parents_re_reg = parent_record.id
                if student_record.response != True:
                    child_data_table += '<td>-</td>'
                    child_data_table += '<td>-</td>'
                    student_record.state = 'awaiting_response'
                elif student_record.confirm != True and student_record.response == True:
                    child_data_table += '<td>No</td>'
                    child_data_table += '<td>-</td>'
                    parent_record.student_ids = [(2, student_record.id)]
                    student_record.state = 'tc_expected'
                elif student_record.confirm == True and student_record.response == True:
                    child_data_table += '<td>Yes</td>'
                    fee_line_id_list = []
                    fee_record = fees_structure_obj.search([
                        ('academic_year_id', '=', student_record.next_year_batch_id.id),
                        ('course_id', '=', student_record.next_year_course_id.id),
                        ('type', '=', 're_reg')], limit=1)
                    if not fee_record.id:
                        raise except_orm(_('Warning!'),
                                         _("Re-Registration Fee is Not Define !"))
                    else:
                        for fee_line_rec in fee_record.fee_line_ids:
                            fee_line_id_list.append(fee_line_rec.id)
                    student_record.write({
                        'state': 'awaiting_re_registration_fee',
                        'fee_status': 're_unpaid',
                    })
                    for fee_line_id in fee_line_id_list:
                        student_record.fees_line_ids = [(4, fee_line_id)]
                    # if student have already paid advance amount
                    student_advance_paid = student_record.name.advance_total_recivable
                    parent_advance_paid = parent_record.name.advance_total_recivable / len(parent_record.student_ids)
                    total_paid = student_advance_paid + parent_advance_paid
                    if total_paid > 0.00:
                        # student_advance_paid = abs(student_advance_paid)
                        s_payble_amount = 0.00
                        is_full_paid = False
                        if student_record.residual > total_paid:
                            s_payble_amount = total_paid
                        else:
                            s_payble_amount = student_record.residual
                            is_full_paid = True
                        if s_payble_amount > 0:
                            self.re_reg_fee_reconcile_stud_advance(re_reg_partner_rec=student_record,
                                                                   amount=s_payble_amount)
                            student_record.total_paid_amount = s_payble_amount
                            if is_full_paid:
                                student_record.fee_status = 're_Paid'
                                student_record.state = 're_registration_confirmed'
                                student_record.name.re_reg_next_academic_year = 'yes'
                            else:
                                student_record.fee_status = 're_partially_paid'
                                student_record.state = 're_registration_confirmed'
                                student_record.name.re_reg_next_academic_year = 'yes'
                    child_data_table += '<td>%s</td>' % (student_record.total_amount)
                child_data_table += '</tr>'
            # if parent paid advance amount then it equaly divide to all children

            # parent_advance_paid = parent_record.name.credit
            # if parent_advance_paid < 0.00:
            #     parent_advance_paid = abs(parent_advance_paid)
            #     if parent_advance_paid >= parent_record.residual:
            #         for s_rec in parent_record.student_ids:
            #             if s_rec.state == 'awaiting_re_registration_fee':
            #                 if s_rec.fee_status != 're_Paid':
            #                     self.re_reg_fee_reconcile_parent_advance(re_student_rec=s_rec,
            #                                                              amount=s_rec.residual,
            #                                                              re_parent_rec=parent_record)
            #                     s_rec.write({'fee_status': 're_Paid', 'total_paid_amount': s_rec.residual, 'state' : 're_registration_confirmed'})
            #                     s_rec.name.re_reg_next_academic_year = 'yes'
            #     else:
            #         count_stud_unpaid = parent_record.student_ids.search_count(
            #             [('re_reg_parents', '=', parent_record.id), ('fee_status', '!=', 're_Paid')])
            #         s_payable = parent_advance_paid / count_stud_unpaid
            #         for s_rec in parent_record.student_ids:
            #             if s_rec.state == 'awaiting_re_registration_fee':
            #                 if s_rec.fee_status != 're_Paid':
            #                     self.re_reg_fee_reconcile_parent_advance(re_student_rec=s_rec,
            #                                                              amount=s_payable,
            #                                                              re_parent_rec=parent_record)
            #                     s_rec.write({'fee_status': 're_partially_paid', 'total_paid_amount': s_payable, 'state' : 're_registration_confirmed'})
            #                     s_rec.name.re_reg_next_academic_year = 'yes'
            flag_state = True
            for student in parent_record.student_ids:
                if student.state in ['awaiting_response']:
                    flag_state = False
            if flag_state == True:
                parent_record.write({'state': 'awaiting_re_registration_fee'})
                
            flag_state_confirm = True
            for student in parent_record.student_ids:
                if student.state in ['awaiting_response','awaiting_re_registration_fee']:
                    flag_state_confirm = False
            if flag_state_confirm == True:
                parent_record.write({'state': 're_registration_confirmed'})

            # send mail to parent for re-reg fee
            if parent_record.residual > 0.00:
                self.send_re_registration_payment_link(parent_record=parent_record,
                                                       child_data_table=child_data_table)
                flag_fee_status = True
                for student in parent_record.student_ids:
                    if student.state in ['awaiting_response'] or student.fee_status in ['re_unpaid']:
                        flag_fee_status = False
                if flag_fee_status == True:
                    parent_record.come_to_confirm()
            elif parent_record.residual == 0.00:
                self.send_re_registration_payment_link(parent_record=parent_record,
                                                       child_data_table=child_data_table)
                if parent_record.state == 'awaiting_re_registration_fee':
                    parent_record.come_to_confirm()
        return True

    @api.multi
    def button_re_registration_confirm(self):
        self.signal_workflow('get_fee_confirm')

    @api.multi
    def come_to_confirm(self):
        for parent_record in self:
            parent_record.write({'state': 're_registration_confirmed'})
#            for student_record in parent_record.student_ids:
#                student_record.state = 're_registration_confirmed'
#                student_record.name.re_reg_next_academic_year = 'yes'


class ReRegistrationResponceStudent(models.Model):
    _name = 're.reg.waiting.responce.student'

    @api.depends('fees_line_ids')
    def compute_amount(self):
        for record in self:
            amount = 0.00
            for fees_record in record.fees_line_ids:
                amount += fees_record.amount
            record.total_amount = amount

    @api.depends('total_amount', 'total_paid_amount')
    def compute_residual_amount_student(self):
        for record in self:
            record.residual = record.total_amount - record.total_paid_amount

    code = fields.Char('Code')
    name = fields.Many2one('res.partner', 'Name')
    reg_no = fields.Char('Registration')
    batch_id = fields.Many2one("batch", "Current Academic Year")
    course_id = fields.Many2one('course', 'Current Admission To Class')
    next_year_batch_id = fields.Many2one("batch", "Next Academic Year")
    next_year_course_id = fields.Many2one('course', 'Next Year Admission To Class')
    re_reg_parents = fields.Many2one('re.reg.waiting.responce.parents', 'Parent')
    parents_re_reg = fields.Many2one('re.reg.waiting.responce.parents', 'Reg Parent')
    confirm = fields.Boolean("Confirm Student")
    fee_status = fields.Selection(
        [('re_unpaid', 'UnPaid'), ('re_partially_paid', 'Partially Paid'), ('re_Paid', 'Paid')], 'Fee Status')
    fees_line_ids = fields.Many2many('fees.line', 're_reg_fee_table', 're_reg_sid', 'fee_id', 'Fees Line')
    state = fields.Selection([('awaiting_response', 'Awaiting Response'),
                              ('awaiting_re_registration_fee', 'Awaiting Re-Registration Fee'), \
                              ('re_registration_confirmed', 'Re-Registration Confirmed'),
                              ('tc_expected', 'TC Expected')])
    total_amount = fields.Float('Total Amount', compute='compute_amount')
    total_paid_amount = fields.Float('Total Paid Amount')
    residual = fields.Float('Balance', compute='compute_residual_amount_student', readonly='1')
    confirmation_date = fields.Date('Confirmed On')
    user_id = fields.Many2one('res.users', 'Confirmed By')
    response = fields.Boolean("Response", default=False)

    @api.multi
    def re_send_payfort_payment_link_student(self):
        if self.residual > 0.00:
            stud_table_data = '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr>' % (
            self.name.name, self.next_year_course_id.name, self.total_amount)
            parent_rec = self.re_reg_parents
            parent_rec.send_re_registration_payment_link(parent_record=parent_rec,
                                                         child_data_table=stud_table_data)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].get('re.reg.student.form') or '/'
        res = super(ReRegistrationResponceStudent, self).create(vals)
        return res

    @api.multi
    def come_tc_expected_to_waiting_fee(self):
        fees_structure_obj = self.env['fees.structure']
        child_data_table = ''
        for re_reg_stud_rec in self:
            fee_line_id_list = []
            fee_record = fees_structure_obj.search([
                ('academic_year_id', '=', re_reg_stud_rec.next_year_batch_id.id),
                ('course_id', '=', re_reg_stud_rec.next_year_course_id.id),
                ('type', '=', 're_reg')], limit=1)
            if not fee_record.id:
                raise except_orm(_('Warning!'),
                                 _("Re-Registration Fee is Not Define !"))
            for fee_line_rec in fee_record.fee_line_ids:
                fee_line_id_list.append(fee_line_rec.id)
            re_reg_stud_rec.write({
                'confirm': True,
                're_reg_parents': re_reg_stud_rec.parents_re_reg.id,
                'state': 'awaiting_re_registration_fee',
                'fee_status': 're_unpaid',
            })
            for fee_line_id in fee_line_id_list:
                re_reg_stud_rec.fees_line_ids = [(4, fee_line_id)]
            # if student have already paid advance amount
            student_advance_paid = re_reg_stud_rec.name.credit
            if student_advance_paid < 0.00:
                student_advance_paid = abs(student_advance_paid)
                s_payble_amount = 0.00
                is_full_paid = False
                if re_reg_stud_rec.residual > student_advance_paid:
                    s_payble_amount = student_advance_paid
                else:
                    s_payble_amount = re_reg_stud_rec.residual
                    is_full_paid = True
                if s_payble_amount > 0:
                    self.re_reg_parents.re_reg_fee_reconcile_stud_advance(re_reg_partner_rec=re_reg_stud_rec,
                                                                          amount=s_payble_amount)
                    re_reg_stud_rec.total_paid_amount = s_payble_amount
                    if is_full_paid:
                        re_reg_stud_rec.write({
                            'fee_status': 're_Paid',
                            're_reg_next_academic_year': 'yes', })
                    else:
                        re_reg_stud_rec.fee_status = 're_partially_paid'
            child_data_table += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr>' % (re_reg_stud_rec.name.name,
                                                                                            re_reg_stud_rec.next_year_course_id.name,
                                                                                            re_reg_stud_rec.total_amount)
            # send mail for fee reminder
            re_reg_stud_rec.parents_re_reg.send_re_registration_payment_link(
                parent_record=re_reg_stud_rec.parents_re_reg,
                child_data_table=child_data_table)

            # if re_reg_stud_rec.fee_status != 're_Paid':
            #     # if parent paid advance amount then it equaly divide to all children
            #     parent_advance_paid = re_reg_stud_rec.re_reg_parents.name.credit
            #     if parent_advance_paid < 0.00:
            #         parent_advance_paid = abs(parent_advance_paid)
            #         if parent_advance_paid > re_reg_stud_rec.re_reg_parents.residual:
            #             # for s_rec in re_reg_stud_rec.re_reg_parents.student_ids:
            #             #     if s_rec.fee_status != 're_Paid':
            #             #         self.re_reg_fee_reconcile_parent_advance(re_student_rec = s_rec,
            #             #                                                  amount = s_rec.residual,
            #             #                                                  re_parent_rec = parent_record)
            #             #         s_rec.write({'fee_status' : 're_Paid','total_paid_amount':s_rec.residual})
            #             #         s_rec.name.re_reg_next_academic_year = 'yes'
            #         else:
            #             # count_stud_unpaid = parent_record.student_ids.search_count([('re_reg_parents','=',parent_record.id),('fee_status','!=','re_Paid')])
            #             # s_payable = parent_advance_paid/count_stud_unpaid
            #             # for s_rec in parent_record.student_ids:
            #             #     if s_rec.fee_status != 're_Paid':
            #             #         self.re_reg_fee_reconcile_parent_advance(re_student_rec = s_rec,
            #             #                                                  amount = s_payable,
            #             #                                                  re_parent_rec = parent_record)
            #             #         s_rec.write({'fee_status' : 're_partially_paid','total_paid_amount':s_payable})


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_re_reg_advance_account(self):
        re_reg_account_rec = self.env['account.account'].search([('code','=','210602')])
        for rec in self:
            if rec.is_student or rec.is_parent:
                if re_reg_account_rec.id:
                    rec.re_reg_advance_account = re_reg_account_rec.id
                else:
                    rec.re_reg_advance_account = False

    @api.depends('advance_total_recivable')
    def get_advance_total_recivable(self):
        """
        -----------------------------------------------------
        :return:
        """
        account_move_line_obj = self.env['account.move.line']
        query = account_move_line_obj._query_get()
        for record in self:
            if record.property_account_customer_advance.id:
                amount_difference = 0.00
                # for account_move_line_rec in account_move_line_obj.search([('partner_id','=',record.id)]):
                #     if account_move_line_rec.account_id.id == record.property_account_customer_advance.id:
                #         amount_difference += account_move_line_rec.credit
                #         amount_difference -= account_move_line_rec.debit
                # record.re_reg_total_recivable = amount_difference
                ctx = self._context.copy()
                ctx['all_fiscalyear'] = True
                query = self.env['account.move.line']._query_get()
                self._cr.execute("""SELECT l.partner_id, SUM(l.debit),SUM(l.credit), SUM(l.debit-l.credit)
                              FROM account_move_line l
                              WHERE l.partner_id IN %s
                              AND l.account_id IN %s
                              AND l.reconcile_id IS NULL
                              AND """ + query +"""
                              GROUP BY l.partner_id
                              """,(tuple(record.ids),tuple(record.property_account_customer_advance.ids),))
                fetch = self._cr.fetchall()
                for pid,total_debit,total_credit,val in fetch:
                    amount_difference += total_credit
                    amount_difference -= total_debit
                    self.advance_total_recivable = amount_difference

    @api.depends('re_reg_total_recivable')
    def get_re_registration_total_recivable(self):
        """
        -----------------------------------------------------
        :return:
        """
        account_move_line_obj = self.env['account.move.line']
        query = account_move_line_obj._query_get()
        for record in self:
            if record.re_reg_advance_account.id:
                amount_difference = 0.00
                # for account_move_line_rec in account_move_line_obj.search([('partner_id','=',record.id)]):
                #     if account_move_line_rec.account_id.id == record.property_account_customer_advance.id:
                #         amount_difference += account_move_line_rec.credit
                #         amount_difference -= account_move_line_rec.debit
                # record.re_reg_total_recivable = amount_difference
                ctx = self._context.copy()
                ctx['all_fiscalyear'] = True
                query = self.env['account.move.line']._query_get()
                self._cr.execute("""SELECT l.partner_id, SUM(l.debit),SUM(l.credit), SUM(l.debit-l.credit)
                              FROM account_move_line l
                              WHERE l.partner_id IN %s
                              AND l.account_id IN %s
                              AND l.reconcile_id IS NULL
                              AND """ + query +"""
                              GROUP BY l.partner_id
                              """,(tuple(record.ids),tuple(record.re_reg_advance_account.ids),))
                fetch = self._cr.fetchall()
                for pid,total_debit,total_credit,val in fetch:
                    amount_difference += total_credit
                    amount_difference -= total_debit
                    self.re_reg_total_recivable = amount_difference

    re_reg_next_academic_year = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Re-registered for next Academic year',
                                                 default='no')
    re_reg_advance_account = fields.Many2one('account.account',
        string="Account Re-Registration Advance",
        help="This account will be used for Re-Registration fee advance payment of Student/Parent",
        compute=_get_re_reg_advance_account)
    re_reg_total_recivable = fields.Float(compute='get_re_registration_total_recivable',string='Re-Reg Advance Total Recivable')
    advance_total_recivable = fields.Float(compute='get_advance_total_recivable',string='Advance Total Recivable')

class FeeStructureInherit(models.Model):
    _inherit = 'fees.structure'

    type = fields.Selection([('reg', 'Registration'), ('re_reg', 'Re-Registration'), ('academic', 'Academic')])


class AccountVoucherInherit(models.Model):
    _inherit = 'account.voucher'

    re_reg_fee = fields.Boolean('is Re-Registration Fee')

    # @api.multi
    # def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     res = super(AccountVoucherInherit, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
    #     if 're_reg_reconcile' in self._context and self._context['re_reg_reconcile']:
    #         account_move_line_obj = self.env['account.move.line']
    #         re_reg_student_obj = self.env['re.reg.waiting.responce.student']
    #         new_cr_line = []
    #         for line_cr in res['value']['line_dr_ids']:
    #             account_move_line_rec = account_move_line_obj.search([('name','=',line_cr['name'])],limit=1)
    #             re_reg_student_rec = re_reg_student_obj.search([('code','=',account_move_line_rec.ref)],limit=1)
    #             if not re_reg_student_rec.id:
    #                 new_cr_line.append(line_cr)
    #         res['value']['line_dr_ids'] = new_cr_line
    #         return res
    #     return res

    # @api.multi
    # def recompute_voucher_lines(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     re_registration_student_obj = self.env['re.reg.waiting.responce.student']
    #     account_move_line_obj = self.env['account.move.line']
    #     invoice_obj = self.env['account.invoice']
    #     res = super(AccountVoucherInherit, self).recompute_voucher_lines(partner_id, journal_id, amount, currency_id, ttype, date)
    #     # if isinstance(partner_id,list):
    #     not_payble_amount_list = []
    #     for res_value in res:
    #         # if res[res_value]['line_dr_ids']:
    #         #     for line_dr_ids_dict in res[res_value]['line_dr_ids']:
    #         #         if isinstance(line_dr_ids_dict, dict):
    #         #             if line_dr_ids_dict['move_line_id']:
    #         #                 account_move_line_rec = account_move_line_obj.browse(line_dr_ids_dict['move_line_id'])
    #         #                 if account_move_line_rec.id:
    #         #                     re_reg_student_rec = re_registration_student_obj.search([
    #         #                         ('code','=',account_move_line_rec.ref)],limit=1)
    #         #                     if re_reg_student_rec.id:
    #         #                         not_payble_amount_list.append((re_reg_student_rec, line_dr_ids_dict['amount_unreconciled']))
    #         line_dr_ids_dub = res[res_value]['line_dr_ids'][:]
    #         linecr_ids_dub = res[res_value]['line_cr_ids'][:]
    #         if len(linecr_ids_dub) > 0:
    #             for line_cr_ids_dict in linecr_ids_dub:
    #                 if isinstance(line_cr_ids_dict, dict):
    #                     # if line_cr_ids_dict['amount'] > 0.00:
    #                         invoice_rec = invoice_obj.search([('number','=',line_cr_ids_dict['name'])],limit=1)
    #                         if invoice_rec.id and invoice_rec.batch_id.id:
    #                             if len(line_dr_ids_dub) > 0:
    #                                 for line_dr_ids_dict in line_dr_ids_dub:
    #                                     if isinstance(line_dr_ids_dict, dict):
    #                                         if line_dr_ids_dict['move_line_id']:
    #                                             account_move_line_rec = account_move_line_obj.browse(line_dr_ids_dict['move_line_id'])
    #                                             if account_move_line_rec.id:
    #                                                 re_reg_student_rec = re_registration_student_obj.search([
    #                                                     ('code','=',account_move_line_rec.ref)],limit=1)
    #                                                 if re_reg_student_rec.id:
    #                                                     if re_reg_student_rec.next_year_batch_id.id != invoice_rec.batch_id.id:
    #                                                         if line_cr_ids_dict['amount'] == line_dr_ids_dict['amount']:
    #                                                             line_cr_ids_dict['amount'] = 0.00
    #                                                             line_dr_ids_dict['amount'] = 0.00
    #                                                             line_dr_ids_dict['reconcile'] = False
    #                                                         elif line_cr_ids_dict['amount'] > line_dr_ids_dict['amount']:
    #                                                             line_cr_ids_dict['amount'] = line_cr_ids_dict['amount'] - line_dr_ids_dict['amount']
    #                                                             line_dr_ids_dict['amount'] = 0.00
    #                                                             line_dr_ids_dict['reconcile'] = False
    #                                                         elif line_cr_ids_dict['amount'] < line_dr_ids_dict['amount']:
    #                                                             line_dr_ids_dict['amount'] = line_dr_ids_dict['amount'] - line_cr_ids_dict['amount']
    #                                                             line_cr_ids_dict['amount'] = 0.00
    #                                                     # not_payble_amount_list.append((re_reg_student_rec, line_dr_ids_dict['amount_unreconciled']))
    #
    #                                 # for reg_amount_dict in not_payble_amount_list:
    #                                 #     if reg_amount_dict[0].next_year_batch_id.id != invoice_rec.batch_id.id:
    #     #     # if res[res_value]['line_cr_ids']:
    #     #     #     res[res_value]['line_cr_ids']
    #     # # student_obj = self.env['res.partner']
    #     # # total_amount = amount
    #     # # # advance payment calculation
    #     # # advance_pay_amount = 0.0
    #     # # if isinstance(partner_id,list):
    #     # #     for res_value in res:
    #     # #         if res[res_value]['line_dr_ids']:
    #     # #             for element in res[res_value]['line_dr_ids']:
    #     # #                 if isinstance(element,dict):
    #     # #                     advance_pay_amount += element['amount_unreconciled']
    #     # #
    #     # # total_amount += advance_pay_amount
    #     # # if isinstance(partner_id,list):
    #     # #     for partner in partner_id:
    #     # #         if student_obj.browse(partner).is_parent != True:
    #     # #             for res_value in res:
    #     # #                 if res[res_value]['line_cr_ids']:
    #     # #                     ele_tuple = []
    #     # #                     ele_dict = []
    #     # #                     for element in res[res_value]['line_cr_ids']:
    #     # #                         if isinstance(element,dict):
    #     # #                             ele_dict.append(element)
    #     # #                         else:
    #     # #                             ele_tuple.append(element)
    #     # #                     if ele_dict:
    #     # #                         for ele_line in sorted(ele_dict, key=lambda k: k['amount_unreconciled']):
    #     # #                             if total_amount == 0:
    #     # #                                 ele_line['amount'] = 0
    #     # #                             else:
    #     # #                                 if ele_line['amount_unreconciled'] > total_amount:
    #     # #                                     ele_line['amount'] = total_amount
    #     # #                                     total_amount = 0
    #     # #                                 else:
    #     # #                                     ele_line['amount'] = ele_line['amount_unreconciled']
    #     # #                                     total_amount -= ele_line['amount_unreconciled']
    #     # #                     line_cr = ele_tuple + ele_dict
    #     # #                     res[res_value]['line_cr_ids'] = line_cr
    #     # #             return res
    #     return res

    # @api.multi
    # def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     res = super(AccountVoucherInherit, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
    #     partner_rec = self.env['res.partner'].browse(partner_id)
    #     account_move_line_obj = self.env['account.move.line']
    #     re_registration_student_obj = self.env['re.reg.waiting.responce.student']
    #     re_registration_parent_obj = self.env['re.reg.waiting.responce.parents']
    #     if 'value' in res:
    #         # if 'line_cr_ids' in res['value']:
    #             # line_cr_ids_list = []
    #             # for line_cr_ids_dict in res['value']['line_cr_ids']:
    #             #     if isinstance(line_cr_ids_dict,dict):
    #             #         if line_cr_ids_dict['move_line_id']:
    #             #             account_move_line_rec = account_move_line_obj.browse(line_cr_ids_dict['move_line_id'])
    #             #             if account_move_line_rec.id:
    #             #                 if partner_rec.id:
    #             #                     if partner_rec.is_student == True:
    #             #                         print "\n\n\nthis is student record"
    #             #                     elif partner_rec.is_parent == True:
    #             #                         print "\n\n\nthis is parent record"
    #             #                     else:
    #             #                         return res
    #
    #         if 'line_dr_ids' in res['value']:
    #             line_dr_ids_list = []
    #             orignal_line_dr_ids_list = res['value']['line_dr_ids']
    #             for line_dr_ids_dict in res['value']['line_dr_ids']:
    #                 if isinstance(line_dr_ids_dict,dict):
    #                     if line_dr_ids_dict['move_line_id']:
    #                         account_move_line_rec = account_move_line_obj.browse(line_dr_ids_dict['move_line_id'])
    #                         if account_move_line_rec.id:
    #                             if partner_rec.id:
    #                                 # print "\n\n2",line_dr_ids_dict['move_line_id'],"\n"
    #                                 if partner_rec.is_student:
    #                                     student_re_reg_rec = re_registration_student_obj.search([('code','=',account_move_line_rec.ref)])
    #                                     if student_re_reg_rec.id:
    #                                         if student_re_reg_rec.next_year_batch_id.id != partner_rec.batch_id.id and\
    #                                                         student_re_reg_rec.next_year_course_id.id != partner_rec.class_id.id:
    #                                             res['value']['line_dr_ids'].pop(res['value']['line_dr_ids'].index(line_dr_ids_dict))
    #                                 elif partner_rec.is_parent:
    #                                     if account_move_line_rec.partner_id.is_student:
    #                                         student_re_reg_rec = re_registration_student_obj.search([('code','=',account_move_line_rec.ref)])
    #                                         if student_re_reg_rec.id:
    #                                             if student_re_reg_rec.next_year_batch_id.id != account_move_line_rec.partner_id.batch_id.id and\
    #                                                             student_re_reg_rec.next_year_course_id.id != account_move_line_rec.partner_id.class_id.id:
    #                                                 line_dr_ids_list.append(line_dr_ids_dict)
    #                                                 # res['value']['line_dr_ids'].pop(res['value']['line_dr_ids'].index(line_dr_ids_dict))
    #             for i in line_dr_ids_list:
    #                 orignal_line_dr_ids_list.pop(orignal_line_dr_ids_list.index(i))
    #
    #             res['value']['line_dr_ids'] = orignal_line_dr_ids_list
    #             return res
    #     return res
