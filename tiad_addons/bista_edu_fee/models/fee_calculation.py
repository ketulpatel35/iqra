import time
from openerp import workflow
from openerp import models, fields, api, _
from datetime import date,datetime,timedelta
import calendar
from openerp.exceptions import except_orm, Warning, RedirectWarning
import hashlib

class Fee_Payment_Line(models.Model):
    """
    Fee Payment Lines
    """
    _name = 'fee.payment.line'
    _description = 'Fee Payment Line'

    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]

    student_id=fields.Many2one('res.partner','Student Name',required=True)
    fee_payment_id=fields.Many2one('fee.payment','Payment ID')
    total_fee=fields.Float('Total Fees')
    date=fields.Date('Date')
    month_id = fields.Many2one('fee.month','Month Ref',store=True)
    month = fields.Selection(List_Of_Month, string='Month')
    year = fields.Char(string="year")

    @api.onchange('month_id')
    def get_year_month(self):
        if self.month_id:
            self.month = self.month_id.name
            self.year = self.month_id.year

class Fee_Payment(models.Model):
    """
    Fee Payment
    """
    _name = 'fee.payment'
    _description = 'Fee Payment'

    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]

    name = fields.Char('Name')
    code = fields.Char('Code')
    course_id= fields.Many2one('course', string='Class', required=True)
    academic_year_id=fields.Many2one('batch','Academic Year' ,required=True)
    fee_payment_line_ids = fields.One2many('fee.payment.line','fee_payment_id','Payment Lines')
    month = fields.Many2one('fee.month', string='Month')
    year = fields.Char('Year', related='month.year')
    fields_readonly = fields.Boolean('make fields Readonly')
    state = fields.Selection([('draft','Draft'),('genarated','Genarated')])

    @api.model
    def create(self,vals):
        recort_exist=self.search([('course_id','=',vals['course_id']),('academic_year_id','=',vals['academic_year_id']),('month','=',vals['month'])])
        if recort_exist.id:
            raise except_orm(_('Warning!'),
                    _("Record is already created for same Month,Year and Class!"))

        return super(Fee_Payment,self).create(vals)

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'genarated':
                raise except_orm(_('Warning!'),
                    _("You can't detete record because Alredy Genarated Fee Payment!"))
        return super(Fee_Payment,self).unlink()

    @api.multi
    def write(self,vals):
        if 'course_id' in vals and vals['course_id']:
            raise except_orm(_('Warning!'),
                    _("You can not Update Data direcaly."))


    # @api.depends('course_id','academic_year_id')
    @api.onchange('month','course_id','academic_year_id')
    def name_code_generate(self):
        name = 'Fee Calculation'
        if self.course_id and self.academic_year_id and self.month:
            name = str(self.course_id.name) + '/' +\
                   str(self.month.name)+ '/' + \
                   str(self.month.year)+ '/' + ' Fee Calculation'
        self.name = name
        self.code = name

    @api.model
    def send_payforts_link(self, student_rec, invoice_rec):
        """
        this method is use to send payfort link for online pay
        fee using payfort payment getway.
        ----------------------------------------------------------------------
        :param student_rec: record set of student
        :param invoice_rec: record set student invoice
        :return:
        """
        advance_paid_amount = 0.00
        move_id_lst = []
        invoice_record = self.env['account.invoice'].search([('partner_id','=',student_rec.id)])
        for inv_rec in invoice_record:
            if inv_rec.payment_ids:
                for payment_rec in inv_rec.payment_ids:
                    for move_rec in payment_rec.move_id:
                        if move_rec.id not in move_id_lst:
                            move_id_lst.append(move_rec.id)
                            for move_line_rec in move_rec.line_id:
                                if student_rec.property_account_customer_advance.id:
                                    if move_line_rec.account_id.id == student_rec.property_account_customer_advance.id:
                                        advance_paid_amount += move_line_rec.credit
                                        advance_paid_amount -= move_line_rec.debit

        # for stud_rec in student_rec.parents1_id.chield1_ids:
        #     for inv_rec in self.env['account.invoice'].search([('partner_id','=',stud_rec.id)]):
        #         if inv_rec.payment_ids:
        #             for payment_rec in inv_rec.payment_ids:
        #                 for move_rec in payment_rec.move_id:
        #                     if move_rec.id not in move_id_lst:
        #                         move_id_lst.append(move_rec.id)
        #                         for move_line_rec in move_rec.line_id:
        #                             if student_rec.property_account_customer_advance.id:
        #                                 if move_line_rec.account_id.id == student_rec.property_account_customer_advance.id:
        #                                     print "credit ==>>>",move_line_rec.credit
        #                                     print "debit====>>>",move_line_rec.debit
        #                                     advance_paid_amount += move_line_rec.credit
        #                                     advance_paid_amount -= move_line_rec.debit

        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'), _("There should be only one payfort record!"))

        if not active_payforts.id:
            raise except_orm(_('Warning!'), _("Please create Payfort Details First!"))

        payfort_amount = invoice_rec.residual
        if payfort_amount > advance_paid_amount:
            # if payfort amount greter then advance payment then mail send for payment
            payfort_amount -= advance_paid_amount
            if active_payforts.charge != 0.00:
                payfort_amount += (payfort_amount * active_payforts.charge) / 100
                payfort_amount += active_payforts.transaction_charg_amount
            total_amount = str(int(round(payfort_amount * 100)))
            invoice_number = invoice_rec.number
            SHA_key = active_payforts.sha_in_key
            PSP_ID = active_payforts.psp_id
            string_input = 'AMOUNT=%s' % (
            total_amount) + SHA_key + 'CURRENCY=AED' + SHA_key + 'LANGUAGE=EN_US' + SHA_key + 'ORDERID=%s' % (
            invoice_number) + SHA_key + 'PSPID=%s'%(PSP_ID) + SHA_key
            ss = 'AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s' % (total_amount, invoice_number, PSP_ID)

            m = hashlib.sha1()
            m.update(string_input)
            hashkey = m.hexdigest()
            hashkey = hashkey.upper()
            link = str(active_payforts.payfort_url) + '?%s&SHASIGN=%s' % (ss, hashkey,)
            # send mail to every student whos pay fee this month
            mail_obj = self.env['mail.mail']
            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([], limit=1)
            mail_data = {
                'email_from': email_sender.smtp_user,
                'email_to': student_rec.parents1_id.parents_email,
                'state': 'outgoing',
                'subject': 'Academic Fee Payment Link',
                'body_html': '<div><p>Dear %s,</p> </br>'
                             '<p>Please find attached the invoice for fee payment for %s'
                             ' in Grade %s and section %s for the current period.'
                             ' You can pay this fees online via the fee payment link below or'
                             ' visit the school fee counter to pay via cash or cheque.'
                             'Online payments via Payfort includes convenience fees charged by'
                             ' the online service provider (Payfort) and the link will display'
                             ' the total value payable. Once paid by you, the receipt for the'
                             ' payment will be emailed to you as confirmation.</p>'
                             '<a href=%s><button>Click For Online Payment</button></a>'
                             '<p>Please note that this invoice does not include unpaid amount from previous invoices.'
                             ' We will send you a separate reminder for any previously unpaid invoices.'
                             " Please contact the school's accounts team via accounts.tiadxb@iqraeducation.net"
                             ' if you need any clarifications.</p>'
                             '<p>Best Regards<br/>'
                             'Registrar<br/>The Indian Academy, Dubai'
                             '<br>Phone : +971 04 2646746, +971 04 2646733, Toll Free: 800 INDIAN (463426)</p>' % (
                             student_rec.parents1_id.name, student_rec.name, student_rec.class_id.name,
                             student_rec.section_id.name, link)}

            mail_id = mail_obj.create(mail_data)
            mail_obj.send(mail_id)

    @api.model
    def get_person_age(self,date_birth, date_today):

        """
        At top level there are three possibilities : Age can be in days or months or years.
        For age to be in years there are two cases: Year difference is one or Year difference is more than 1
        For age to be in months there are two cases: Year difference is 0 or 1
        For age to be in days there are 4 possibilities: Year difference is 1(20-dec-2012 - 2-jan-2013),
        """
        years_diff = date_today.year - date_birth.year

        months_diff = 0
        if date_today.month >= date_birth.month:
            months_diff = date_today.month - date_birth.month
        else:
            years_diff -= 1
            months_diff = 12 + (date_today.month - date_birth.month)

        days_diff = 0
        if date_today.day >= date_birth.day:
            days_diff = date_today.day - date_birth.day
        else:
            months_diff -= 1
            days_diff = 31 + (date_today.day - date_birth.day)

        if months_diff < 0:
            months_diff = 11
            years_diff -= 1

        age = years_diff
        age_dict = {
            'years' : years_diff,
            'months' : months_diff,
            'days' : days_diff
        }
        print age_dict
        return age_dict

    @api.model
    def months_between(self,start_date,end_date):
        months = []
        month_year = []
        cursor = start_date

        while cursor <= end_date:
            if cursor.month not in months:
                months.append(cursor.month)
                month_year.append((int(cursor.month),int(cursor.year)))
            cursor += timedelta(weeks=1)
        return month_year

    @api.multi
    def generate_fee_payment(self):
        """
        this method use to monthly fee calculation(including discount),
        --> calculate monthly total amount of fee pay to student,
            and display in student monthaly pay line,(current form)
        --> also calculate student remaining payment in student
            fee pay detail,(student form)
        --> also create invoice of student with different payment
            by student(account)
        --> send mail to student for pay fee from payfort.
        --------------------------------------------------------
        @param self : object pointer
        """
        main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
                                                                   ('leave_month','=',False)])
        leave_month = []
        for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),('leave_month','=',True)]):
            leave_month.append((int(l_month.name),int(l_month.year)))
        invoice_obj = self.env['account.invoice']
        student_obj = self.env['res.partner']
        month_year_obj = self.month

        if self.month.leave_month == True:
            # get worning if try to calculate fee for leave month
            raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))

        self.fields_readonly=True

        if month_year_obj.id:
            for stud_id in student_obj.search([('is_parent', '=', False),
                                               ('is_student','=',True),
                                               ('active','=',True),
                                               ('ministry_approved','=',True),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id)]):
                month_diff = main_month_diff
                joining_date = datetime.strptime(stud_id.admission_date,"%Y-%m-%d").date()
                start_date = datetime.strptime(self.academic_year_id.start_date,"%Y-%m-%d").date()
                get_unpaid_diff = self.get_person_age(start_date,joining_date)
                month_in_stj = self.months_between(start_date,joining_date)
                unpaid_month = 0
                if get_unpaid_diff.get('months') > 0:
                    unpaid_month = get_unpaid_diff.get('months')
                    if len(month_in_stj) > 0 and len(leave_month) > 0:
                        for leave_month_year in leave_month:
                            if leave_month_year in month_in_stj:
                                unpaid_month -= 1

                month_diff -= unpaid_month
                if stud_id.id:
                    fee_month_amount = 0.00
                    total_discount = 0.00
                    fee_line_lst = []
                    invoice_dic={}

                    for fee_amount in stud_id.student_fee_line:
                        per_month_year_fee = 0.0
                        dis_amount = 0.00
                        if fee_amount.fee_pay_type.name == 'year':
                            exist_month = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
                            if exist_month == 0:
                                all_amount = stud_id.student_fee_line.search([('name','=',fee_amount.name.id),
                                                                              ('stud_id','=',stud_id.id)],limit=1)
                                per_month_year_fee = all_amount.amount
                                if fee_amount.discount > 0:
                                    dis_amount = (per_month_year_fee * fee_amount.discount)/100
                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income.id,
                                            'name' : fee_amount.name.name,
                                            'quentity' : 1.00,
                                            'price_unit' : round(per_month_year_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_year_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_alt_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
                                                                    'discount_amount' : dis_amount,
                                                                    'month_id':month_year_obj.id})
                                else:
                                    fee_year_pay_value = {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': per_month_year_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : dis_amount,
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'quater':
                            if month_year_obj.qtr_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('qtr_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                    if exist_month.id:
                                        count_month += 1

                                if count_month != 0:
                                    new_per_month_qtr_fee = per_month_qtr_fee * count_month
                                    if all_amount.cal_amount <= new_per_month_qtr_fee:
                                        cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                        if cal_alt_new > 0:
                                            per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                        else:
                                            per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                else:
                                    per_month_qtr_fee = all_amount.total_amount/(month_diff/3)

                                fee_month_amount += per_month_qtr_fee

                                # discount calculation for quater month
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                if fee_amount.discount > 0:
                                    if fee_paid_line > 0:
                                        if amount_above.discount_amount > 0.0:
                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                            current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
                                            if alredy_permonth_discount == current_month_disamount:
                                                dis_amount = current_month_disamount
                                            elif alredy_permonth_discount < current_month_disamount:
                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount + difference_discount
                                            elif alredy_permonth_discount > current_month_disamount:
                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount - difference_discount
                                        else:
                                            dis_amount_quater = (per_month_qtr_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_quater + (dis_amount_quater * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
                                total_discount += dis_amount

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income.id,
                                            'name' : fee_amount.name.name,
                                            'quentity' : 1.00,
                                            'price_unit' : round(per_month_qtr_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_qtr_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_qtr_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                        if fee_amount.fee_pay_type.name == 'half_year':
                            if month_year_obj.quater_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_qtr_fee = all_amount.total_amount/2
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('quater_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                    if exist_month.id:
                                        count_month += 1
                                if count_month != 0:
                                    new_per_month_qtr_fee = per_month_qtr_fee * count_month

                                    if all_amount.cal_amount <= new_per_month_qtr_fee:
                                        cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                        if cal_alt_new > 0:
                                            per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                        else:
                                            per_month_qtr_fee = all_amount.total_amount/2
                                else:
                                    per_month_qtr_fee = all_amount.total_amount/2

                                fee_month_amount += per_month_qtr_fee

                                #discount calculation for half year
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                if fee_amount.discount > 0:
                                    if fee_paid_line > 0:
                                        if amount_above.discount_amount > 0.0:
                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                            current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
                                            if alredy_permonth_discount == current_month_disamount:
                                                dis_amount = current_month_disamount
                                            elif alredy_permonth_discount < current_month_disamount:
                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount + difference_discount
                                            elif alredy_permonth_discount > current_month_disamount:
                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount - difference_discount
                                        else:
                                            dis_amount_half_month = (per_month_qtr_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_half_month + (dis_amount_half_month * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_qtr_fee * fee_amount.discount)/100

                                total_discount += dis_amount

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income.id,
                                            'name' : fee_amount.name.name,
                                            'quentity' : 1.00,
                                            'parent_id' : stud_id.parents1_id.id,
                                            'price_unit' : round(per_month_qtr_fee,2),
                                            'rem_amount' : round(per_month_qtr_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_qtr_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }

                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'alt_month':
                            if month_year_obj.alt_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('alt_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                    if exist_month.id:
                                        count_month += 1
                                if count_month != 0:
                                    new_per_month_alt_fee = per_month_alt_fee * count_month
                                    if all_amount.cal_amount <= new_per_month_alt_fee:
                                        cal_alt_new = new_per_month_alt_fee - all_amount.cal_amount
                                        if cal_alt_new > 0:
                                            per_month_alt_fee = per_month_alt_fee + cal_alt_new
                                        else:
                                            per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                else:
                                    per_month_alt_fee = all_amount.total_amount/(month_diff/2)

                                fee_month_amount += per_month_alt_fee

                                # discount calculation for alt month
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                if fee_amount.discount > 0:
                                    if fee_paid_line > 0:
                                        if amount_above.discount_amount > 0.0:
                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                            current_month_disamount = (per_month_alt_fee * fee_amount.discount)/100
                                            if alredy_permonth_discount == current_month_disamount:
                                                dis_amount = current_month_disamount
                                            elif alredy_permonth_discount < current_month_disamount:
                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount + difference_discount
                                            elif alredy_permonth_discount > current_month_disamount:
                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount - difference_discount
                                        else:
                                            dis_amount_alt_month = (per_month_alt_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_alt_month + (dis_amount_alt_month * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_alt_fee * fee_amount.discount)/100

                                total_discount += dis_amount

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income.id,
                                            'name' : fee_amount.name.name,
                                            'quentity' : 1.00,
                                            'price_unit' : round(per_month_alt_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_alt_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))
                                exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_alt_pay_detail.id:
                                    if exist_alt_pay_detail.month_id.id != month_year_obj.id:
                                        exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_alt_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + round(per_month_alt_fee,2),
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'month':
                            amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                          ('student_id','=',stud_id.id)],limit=1)
                            # per month fee calculation
                            per_month_fee = amount_above.total_amount/(month_diff)
                            # already fee paided month
                            fee_paid_line = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
                            if fee_paid_line > 0:
                                new_rem_amount = per_month_fee * fee_paid_line
                                if amount_above.cal_amount <= new_rem_amount:
                                    cal_new = new_rem_amount - amount_above.cal_amount
                                    if cal_new > 0:
                                        per_month_fee = cal_new + per_month_fee
                                    else:
                                        per_month_fee = amount_above.total_amount/(month_diff)
                            else:
                                per_month_fee = amount_above.total_amount/(month_diff)
                            fee_month_amount += per_month_fee

                            # discount calculation for per month
                            if fee_amount.discount > 0:
                                if fee_paid_line > 0:
                                    if amount_above.discount_amount > 0.0:
                                        alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                        current_month_disamount = (per_month_fee * fee_amount.discount)/100
                                        if alredy_permonth_discount == current_month_disamount:
                                            dis_amount = current_month_disamount
                                        elif alredy_permonth_discount < current_month_disamount:
                                            difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                            difference_discount = difference_discount_per_month * fee_paid_line
                                            dis_amount = current_month_disamount + difference_discount
                                        elif alredy_permonth_discount > current_month_disamount:
                                            difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                            difference_discount = difference_discount_per_month * fee_paid_line
                                            dis_amount = current_month_disamount - difference_discount
                                    else:
                                        dis_amount_month = (per_month_fee * fee_amount.discount)/100
                                        dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
                                else:
                                    dis_amount = (per_month_fee * fee_amount.discount)/100

                            total_discount += dis_amount

                            fee_line_lst.append((0,0,
                                {
                                    'product_id' : fee_amount.name.id,
                                    'account_id' : fee_amount.name.property_account_income.id,
                                    'name' : fee_amount.name.name,
                                    'quentity' : 1.00,
                                    'price_unit' : round(per_month_fee,2),
                                    'parent_id' : stud_id.parents1_id.id,
                                    'rem_amount' : round(per_month_fee,2),
                                    'priority' : fee_amount.sequence,
                                }))

                            exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                   ('student_id','=',stud_id.id)], limit=1)
                            if exist_stud_pay_detail.id:
                                if exist_stud_pay_detail.month_id.id != month_year_obj.id:
                                    exist_stud_pay_detail.write({'cal_amount':amount_above.cal_amount + per_month_fee,
                                                                 'discount_amount':amount_above.discount_amount + dis_amount,
                                                                 'month_id': month_year_obj.id,})
                            else:
                                fee_pay_value =\
                                    {
                                        'name': fee_amount.name.id,
                                        'student_id': stud_id.id,
                                        'month_id': month_year_obj.id,
                                        'fee_pay_type': fee_amount.fee_pay_type,
                                        'cal_amount': amount_above.cal_amount + per_month_fee,
                                        'total_amount' : fee_amount.amount,
                                        'discount_amount' : amount_above.discount_amount + dis_amount
                                    }

                                stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'term':
                            paid_term_obj = self.env['paid.term.history']
                            terms=self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])

                            amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                          ('student_id','=',stud_id.id)])
#
                            current_term=amount_above.next_term

                            exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                   ('student_id','=',stud_id.id)])

                            per_month_fee=0
                            term_id=False
#                            prev_term_seq=exist_stud_pay_detail.next_term.seq
#                            same_seq_terms=self.env['acd.term'].search([('seq','=',prev_term_seq+1)])\
                            prev_term_seq=exist_stud_pay_detail.next_term.id

                            if prev_term_seq:
                                same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq)])

                            next_term=exist_stud_pay_detail.next_term.id
                            invoice_dic={}
                            if amount_above.next_term.id:
                                start_date=datetime.strptime(current_term.start_date, "%Y-%m-%d")

                                if start_date.month == self.month.name:
                                    if int(start_date.year) == int(self.year):
                                        per_month_fee = fee_amount.amount / len(terms)

                                        if len(stud_id.paid_term_history_ids) > 0:
                                            new_per_month_fee = per_month_fee * len(stud_id.paid_term_history_ids)
                                            if exist_stud_pay_detail.cal_amount <= new_per_month_fee:
                                                cal_diff = new_per_month_fee - exist_stud_pay_detail.cal_amount
                                                if cal_diff > 0:
                                                    per_month_fee += cal_diff
                                                else:
                                                    per_month_fee = fee_amount.amount / len(terms)
                                        else:
                                            per_month_fee = fee_amount.amount / len(terms)
                                        term_id=amount_above.next_term.id
                                        prev_paid_rec=paid_term_obj.search([('student_id','=',stud_id.id),('term_id','=',term_id),('batch_id','=',self.academic_year_id.id)])
                                        if not prev_paid_rec:
                                            paid_term_obj.create({'student_id':stud_id.id,'term_id':term_id,'batch_id':self.academic_year_id.id})
                                        if same_seq_terms.ids:
                                            list=[]
                                            for each in same_seq_terms:
                                                if each in terms:
                                                    list.append(each.id)
#                                                    next_term=each.id

                                            if list:
                                                list=sorted(list)
                                                next_term=list[0]
                                    else:
                                        per_month_fee=0
                                        term_id=False

                            #discount calculation

                            if fee_amount.discount > 0:
                                if fee_paid_line > 0:
                                    if amount_above.discount_amount > 0.0:
                                        alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                        current_month_disamount = (per_month_fee * fee_amount.discount)/100
                                        if alredy_permonth_discount == current_month_disamount:
                                            dis_amount = current_month_disamount
                                        elif alredy_permonth_discount < current_month_disamount:
                                            difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                            difference_discount = difference_discount_per_month * fee_paid_line
                                            dis_amount = current_month_disamount + difference_discount
                                        elif alredy_permonth_discount > current_month_disamount:
                                            difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                            difference_discount = difference_discount_per_month * fee_paid_line
                                            dis_amount = current_month_disamount - difference_discount
                                    else:
                                        dis_amount = (per_month_fee * fee_amount.discount)/100
                                else:
                                    dis_amount = (per_month_fee * fee_amount.discount)/100

                            total_discount += dis_amount
                            fee_month_amount += per_month_fee

                            fee_line_lst.append((0,0,
                                    {
                                        'product_id' : fee_amount.name.id,
                                        'account_id' : fee_amount.name.property_account_income.id,
                                        'name' : fee_amount.name.name,
                                        'quentity' : 1.00,
                                        'price_unit' : round(per_month_fee,2),
                                        'rem_amount' : round(per_month_fee,2),
                                        'parent_id' : stud_id.parents1_id.id,
                                        'priority' : fee_amount.sequence,
                                    }))

                            fee_pay_value =\
                                        {
                                            'name': fee_amount.name.id,
                                            'student_id': stud_id.id,
                                            'month_id': month_year_obj.id,
                                            'fee_pay_type': fee_amount.fee_pay_type.name,
                                            'cal_amount': amount_above.cal_amount + per_month_fee,
                                            'total_amount' : fee_amount.amount,
                                            'next_term':next_term,
                                            'discount_amount' : amount_above.discount_amount + dis_amount,
                                        }
                            invoice_dic.update({'term_id':term_id or "",})
                            if not exist_stud_pay_detail.id:
                                stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
                            else:
                                for val in exist_stud_pay_detail:
                                    val.cal_amount=amount_above.cal_amount + per_month_fee
                                    val.next_term=next_term
                                    val.discount_amount = amount_above.discount_amount + dis_amount

                        if fee_amount.discount > 0.00 and dis_amount != 0.00:
                            if not fee_amount.name.fees_discount:
                                raise except_orm(_("Warning!"), _('Please define Discount Fee For %s.')%(fee_amount.name.name))
                            else:
                                if not fee_amount.name.fees_discount.property_account_income.id:
                                    raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_amount.name.fees_discount.name))
                                else:
                                    fee_line_lst.append((0,0,{
                                        'product_id' : fee_amount.name.fees_discount.id,
                                        'account_id' : fee_amount.name.fees_discount.property_account_income.id,
                                        'name' : fee_amount.name.fees_discount.name,
                                        'quantity' : 1.00,
                                        'price_unit' : -round(dis_amount,2),
                                        'rem_amount' : -round(dis_amount,2),
                                        'priority' : 0,
                                        }))

                    # Monthaly Fee Pyment Generate Line
                    exist_fee_line = self.fee_payment_line_ids.search([('student_id','=',stud_id.id),
                                                                        ('month_id','=',self.month.id),
                                                                        ('year','=',self.year),
                                                                        ('fee_payment_id','=',self.id)])
                    if not exist_fee_line.id:
                        self.fee_payment_line_ids.create({
                            'student_id': stud_id.id,
                            'total_fee': fee_month_amount-total_discount,
                            'month_id': month_year_obj.id,
                            'month': month_year_obj.name,
                            'year': month_year_obj.year,
                            'fee_payment_id' : self.id,
                            })
                    # else:
                    #     exist_fee_line.write({
                    #         'total_fee': fee_month_amount-total_discount,
                    #     })

                    # Invoice Create
                    exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month_year_obj.id)])
                    if exist_invoice == 0:
                        invoice_vals = {
                                'partner_id' : stud_id.id,
                                'month_id' : month_year_obj.id,
                                'account_id' : stud_id.property_account_receivable.id,
                                'invoice_line' : fee_line_lst,
                                'month' : month_year_obj.name,
                                'year' : month_year_obj.year,
                                'batch_id' : self.academic_year_id.id,
                            }
                        invoice_id = invoice_obj.create(invoice_vals)

                        if invoice_dic:
                            invoice_id.write(invoice_dic)

                        # Invoice validate
                        invoice_id.signal_workflow('invoice_open')

                        # send payfort link for online fee payment
                        if invoice_id.id:
                            self.send_payforts_link(student_rec = stud_id,invoice_rec=invoice_id)

                    fee_status = stud_id.payment_status.search([('month_id','=',month_year_obj.id),
                                                                ('student_id','=',stud_id.id)])
                    if not fee_status.id:
                        status_val = {
                            'month_id': month_year_obj.id,
                            'paid': False,
                        }
                        stud_id.payment_status = [(0,0,status_val)]
            self.state = 'genarated'
        else:
            raise except_orm(_('Warning !'),
                    _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                             % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))