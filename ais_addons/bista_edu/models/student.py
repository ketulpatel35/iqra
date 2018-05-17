# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date,datetime,timedelta
import time
from openerp.exceptions import except_orm

class Student(models.Model):

    _inherit = 'res.partner'

    @api.depends('parent1_id')
    def get_sibling(self):
        """
        get sibling
        ------------------
        :return:
        """
        for stud_rec in self:
            sibling_list = []
            if stud_rec.parents1_id.id:
                for child_rec in stud_rec.parents1_id.chield1_ids:
                    if not child_rec.id == stud_rec.id:
                        sibling_list.append(child_rec.id)
            stud_rec.sibling_ids = [(6,0,sibling_list)]

    parent1_id = fields.Char('Parent Code')
    student_id = fields.Char('Student ID') 
    reg_no = fields.Char('Registration Number')
    class_id = fields.Many2one('course',string="Class")
    year_id = fields.Many2one('batch',string='Year')
    is_parent = fields.Boolean('is Parents')
    is_student = fields.Boolean('is Student')
    chield1_ids = fields.One2many('res.partner','parents1_id','Child')
    mother_name = fields.Char('Mother name')
    parents_email = fields.Char('Father Email')
    mother_email = fields.Char('Mother Email')
    parent_profession = fields.Char()
    mother_profession = fields.Char()
    parent_contact = fields.Char('Father Contact')
    mother_contact = fields.Char('Mother Contact')
    student_fee_line = fields.Many2many('fees.line','student_id','fee_line_id',string='Student Fees')
    parents1_id = fields.Many2one('res.partner','Parents',domain=[('is_parent','=',True)])
#    student_name = fields.Char('Student Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    admission_date = fields.Date(string='Admission Date')
    batch_id = fields.Many2one('batch', 'Academic Year')
    course_id = fields.Many2one('course', 'Admission To Class')
    # standard_id = fields.Many2one('standard', 'Admitted Class')
    # category_id = fields.Many2one('category', string='Category')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender')
    emirati = fields.Selection([('y', 'Yes'), ('n', 'No')], string='Emirati')
    arab = fields.Selection([('arab', 'Arabs'), ('non_arab', 'Non Arabs')], string='Arab')
    religion_id = fields.Many2one('religion', string='Religion')
    birth_date = fields.Date(string='Birth Date')
    # birth_place = fields.Many2one('res.country.state', string='City')
    birth_place = fields.Char(string='City')
    birth_country = fields.Many2one('res.country', string='Birth Country')
    emirates_id = fields.Char('Emirates Id')
    passport_issue_date = fields.Date(string='Passport issue date')
    # student_id = fields.Char(sring='Student Id')
    title = fields.Many2one('res.partner.title', 'Title')
    date_of_joining = fields.Date('Date Of Joining')
    student_section_id = fields.Many2one('section', 'Admitted section')
    section_id = fields.Many2one('crm.case.section')
    # application_number = fields.Char(size=16, string='Application Number')
    # application_date = fields.Datetime(string='Application Date')
    phone = fields.Char(size=16, string='Phone')
    mobile = fields.Char(size=16, string='Mobile')
    email = fields.Char(size=256, string='Email')
    prev_institute = fields.Char(size=256, string='Previous Institute')
    # prev_course = fields.Char(size=256, string='Previous Course')
    # prev_result = fields.Char(size=256, string='Previous Result')
    family_business = fields.Char(size=256, string='Family Business')
    family_income = fields.Float(string='Family Income')
    passport_no = fields.Char('Passport Number', size=128)
    place_of_issue = fields.Many2one('res.country', string='Place Of Issue')
    passport_expiry_date = fields.Date(string='Passport expiry date')
    visa_no = fields.Char('Visa Number', size=128)
    visa_issue_date = fields.Date(string='Visa issue date')
    visa_expiry_date = fields.Date(string='Visa expiry date')
    lang_id = fields.Many2one('res.lang', 'Languange')
    other_lang_id = fields.Many2one('res.lang', 'Other Languange')
    emergency_contact = fields.Char("Emergency Contact")
    prev_institute = fields.Char(size=256, string='Previous Institute')
    prev_grade = fields.Char(size=256, string='Grade Last attended')
    last_attendance = fields.Date(string='Last date of attendance')
    prev_academic_year = fields.Many2one('batch', 'Previous Academic Year')
    prev_academic_city = fields.Char(size=64, string='City')
    prev_academic_country = fields.Many2one('res.country', string='Country')
    tranfer_reason = fields.Text('Reason for Transfer')
    remarks = fields.Text('Remarks')
    about_us = fields.Selection(
        [('fb', 'facebook'), ('google', 'Google'), ('friend', 'Family & Friends'),
         ('sms_camp','SMS campaign'), ('np', 'Newspaper'),('visitnearbyarea','Visit to nearby area'),
         ('marketing_leaflet','Marketing Leaflet'),('other','Other')],
        string='Where did you first find out about us?')
    curriculum = fields.Char("Curriculum")
    t_c_number = fields.Char("TC Number")
    blood_group = fields.Char("Blood Group")
    s_height = fields.Char("Height(In Cm)")
    s_width = fields.Char("Weight(In Kg)")
    child_allergic = fields.Boolean("Is your child allergic to anything?")
    w_allergic = fields.Char("What is your child allergic to?")
    w_reaction = fields.Char("What is the reaction?")
    w_treatment = fields.Char('What is the treatment?')
    under_medication = fields.Boolean('Is your child currently under medication / treatment?')
    w_medication_mention = fields.Char('Please Mention')
    w_treatment_mention = fields.Char('What is the treatment?')
    transport_type = fields.Selection([('own', 'Own Transport'), ('school', 'School Transport')], 'Transport Type')
    bus_no = fields.Char('Bus No')
    pick_up = fields.Char('Pick up')
    droup_off_pick = fields.Char("Drop off points")
    transfer_certificate = fields.Binary('Transfer Certificate(Scanned copy)')
    s_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    s_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    passport_copy1 = fields.Binary('Passport Copy Page 1(Scanned copy)')
    passport_copy2 = fields.Binary('Passport Copy Page 2(Scanned copy)')
    parent_visa_copy = fields.Binary('Visa Copy(Scanned copy)')
    f_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    f_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    mother_visa_copy = fields.Binary('Visa Copy(Scanned copy)')
    m_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    m_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    medical_documents_file = fields.Binary("Medical documents/file")
    #sibling_ids = fields.One2many('sibling','student_id',string='Sibling')
    sibling_ids = fields.Many2many('res.partner',string='Sibling',compute='get_sibling')
    nationality = fields.Many2one('res.country',string="Nationality")
    parents_office_contact = fields.Char("Parents Office Contact")
    mother_office_contact = fields.Char("Mother Office Contact")
    parent_address = fields.Text("Parents Address")
    mother_address = fields.Text("Mother Address")
#    student_fee_line = fields.One2many('fees.line','stud_id','Fee Lines')
    student_fee_line = fields.One2many('fees.line','stud_id','Fee Lines')
    payble_fee_ids = fields.One2many('student.payble.fee','student_id',string="Payble Fee")
    paid_term_history_ids = fields.One2many('paid.term.history','student_id',sring="Piad Term History")
    payment_status = fields.One2many('student.fee.status','student_id',string='Fee Status')
    discount_on_fee = fields.Many2one('discount.category',string='Fee Discount')
    ministry_approved = fields.Boolean('Ministry Approval')
    waiting_approval = fields.Boolean('Waiting Ministry Approval')
    isd_code = fields.Char('ISD Code')
    about_us_other = fields.Char('Others')
    is_old_student = fields.Boolean('Old Student')
    old_id = fields.Char('Old Id')
    is_old_parent = fields.Boolean('Old Parents')
    stud_batch_shift = fields.Selection([('morning', 'Morning Batch'), ('clb', 'CLB Batch')],
                                    select=True, string='Batch Shift')
    khada_sis = fields.Char('KHDA/SIS')
    school_remark = fields.Char('Partner Remarks')

    _sql_constraints = [
        ('khada_sis_unique', 'unique(khada_sis)', 'KHDA/SIS must be unique per Student !')
        ]

    #------------------------------------------------- TERM STARTS ---------------------------------------------------
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

    @api.multi
    def ais_student_term_wise_fee_updation(self):
        invoice_obj = self.env['account.invoice']
        voucher_obj = self.env['account.voucher']
        for student_rec in self.search([('is_student','=',True),('is_old_student','=',True)]):
            fee_line_lst = []
            total_advance_amount = 0
            for fee_detail_line in student_rec.payble_fee_ids:
                if fee_detail_line.fee_pay_type.name != 'term':
                    fee_line_lst.append((0,0,{
                                        'product_id' : fee_detail_line.name.id,
                                        'account_id' : fee_detail_line.name.property_account_income.id,
                                        'name' : fee_detail_line.name.name,
                                        'quantity' : 1.00,
                                        'price_unit' : fee_detail_line.total_amount,
                                        'rem_amount' : fee_detail_line.total_amount,
                                        'priority' : 0,
                                        }))
                    fee_detail_line.cal_amount = fee_detail_line.total_amount
                elif fee_detail_line.fee_pay_type.name == 'term':
                    terms = self.env['acd.term'].search([('batch_id', '=', self.batch_id.id)])
                    if len(terms) > 0:
                        term_list = []
                        for_next_term = self.env['acd.term'].search([('id', '>', terms[0].id)])
                        for term_rec in for_next_term:
                            term_list.append(term_rec.id)
                        if term_list:
                            term_list= sorted(term_list)
                            next_term = term_list[0]
                        no_of_month = 0
                        term_start_date = datetime.strptime(terms[0].start_date,"%Y-%m-%d").date()
                        term_end_date = datetime.strptime(terms[0].end_date,"%Y-%m-%d").date()
                        no_of_month = self.months_between(term_start_date,term_end_date)
                        amount = fee_detail_line.total_amount
                        month_diff_term = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),('leave_month','=',False)])
                        term_amount = amount / (month_diff_term)
                        term_cal_amount = 0
                        if len(no_of_month) > 0:
                            term_cal_amount = term_amount * len(no_of_month)
                        term2_start_date = datetime.strptime(terms[1].start_date,"%Y-%m-%d").date()
                        term2_end_date = datetime.strptime(terms[1].end_date,"%Y-%m-%d").date()
                        no2_of_month = self.months_between(term2_start_date,term2_end_date)
                        term2_cal_amount = 0
                        if len(no2_of_month) > 0:
                            term2_cal_amount = term_amount * len(no2_of_month)
                        total_term_cal = term_cal_amount + term2_cal_amount
                        inv_amount = 0.00
                        if fee_detail_line.cal_turm_amount < total_term_cal:
                            inv_amount = fee_detail_line.cal_turm_amount
                        else:
                            inv_amount = total_term_cal
                        fee_line_lst.append((0,0,{
                                        'product_id' : fee_detail_line.name.id,
                                        'account_id' : fee_detail_line.name.property_account_income.id,
                                        'name' : fee_detail_line.name.name,
                                        'quantity' : 1.00,
                                        'price_unit' : inv_amount,
                                        'rem_amount' : inv_amount,
                                        'priority' : 0,
                                        }))
                        if fee_detail_line.cal_turm_amount > total_term_cal:
                            advance_amount = fee_detail_line.cal_turm_amount - total_term_cal
                            total_advance_amount += advance_amount

                        fee_detail_line.cal_amount = total_term_cal
                        # fee_detail_line.cal_turm_amount = total_term_cal
                        fee_detail_line.next_term = terms[2]
            current_date = datetime.today()
            month_rec = self.env['fee.month'].search([('batch_id','=',self.batch_id.id),
                                                      ('name','=',current_date.month),
                                                      ('year','=',current_date.year)])
            # invoice create
            invoice_vals = {
                'partner_id' : student_rec.id,
                'month_id' : month_rec.id,
                'account_id' : student_rec.property_account_receivable.id,
                'invoice_line' : fee_line_lst,
                'month' : month_rec.name,
                'year' : month_rec.year,
                'batch_id' : self.batch_id.id,
            }
            invoice_id = invoice_obj.create(invoice_vals)

            #Voucher Create
            if not student_rec.property_account_customer_advance.id:
                            raise except_orm(_('Warning!'),
                                _("Please create Payfort Details First!") )
            journal_rec = self._get_journal()
            voucher_data = {
                'period_id': self._get_period().id,
                'account_id': journal_rec.default_debit_account_id.id,
                'partner_id': student_rec.id,
                'journal_id': journal_rec.id,
                'currency_id': self._get_currency(),
                'reference': 'Term Script',
                'amount': total_advance_amount,
                'type': 'receipt',
                'state': 'draft',
                'pay_now': 'pay_later',
                'name': '',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': 1,
                'tax_id': False,
                'payment_option': 'without_writeoff',
                'comment': _('Write-Off'),
                'advance_account_id':student_rec.property_account_customer_advance.id,
                }
            voucher_id = voucher_obj.create(voucher_data)
            student_fee_status = self.env['student.fee.status'].create(
                {'month_id':month_rec.id,
                 'name':month_rec.name,
                 'year':month_rec.year,
                 'student_id':student_rec.id,
                 'paid' : False,
                 })
            student_rec.ministry_approved = True
    # -------------------------------------------TERM OVER ------------------------------------------------------------

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if 'active_ids' in self._context and self._context['active_ids']:
            for record in self.env['res.partner'].browse(self._context['active_ids']):
                mod_obj = self.pool.get('ir.model.data')
                if view_type == 'form':
                    if record.is_student == True or record.is_parent == True:
                        vid = mod_obj.get_object_reference(self._cr,self._uid,'bista_edu', 'view_student_parent_form')
                        vid = vid and vid[1] or False,
                        view_id = vid
                        return super(Student, self).fields_view_get(
                                view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        return super(Student, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    @api.model
    def create(self,vals):
        """
        add unique student id when create student.
        --------------------------------------
        :param vals:
        :return:
        """
        if 'is_student' in vals and vals['is_student']:
            vals['student_id'] = self.env['ir.sequence'].get('res.partner')
        return super(Student, self).create(vals)

    @api.model
    def write_on_registration(self, vals):
        """
        student master data sink with registration table
        :param vals:
        :return:
        """
        if self.reg_no:
            registration_rec = self.env['registration'].search([('enquiry_no','=',self.reg_no)],limit=1)
            if registration_rec.id:
                registration_rec.write(vals)
                if vals.has_key('stud_batch_shift'):
                    registration_rec.batch_shift = vals['stud_batch_shift']
        return True

    @api.multi
    def write(self, vals):
        """
        overide write method
        ---------------------
        :param vals:
        :return:
        """
        for rec in self:
            if rec.is_student:
                rec.write_on_registration(vals)
            if rec.is_parent:
                for child in rec.chield1_ids:
                    child.write(vals)
        return super(Student, self).write(vals)


    @api.multi
    def name_get(self):
        res = []
        for record in self:
            _name = ''
            f_name = str(record.name) if str(record.name) != 'False' else ""
            m_name = str(record.middle_name) if str(record.middle_name) != 'False' else ""
            l_name = str(record.last_name) if str(record.last_name) != 'False' else ""
            if record.is_parent == True:
                _name = '[ ' + str(record.parent1_id) + ' ]' + f_name + ' ' + m_name + ' ' + l_name
            elif record.is_student == True:
                _name = '[ ' + str(record.student_id) + ' ]' + f_name + ' ' + m_name + ' ' + l_name
            else:
                _name = str(record.name)
            res.append((record.id, _name))
        return res

    @api.multi
    def update_advance_account(self):
        fee_line_obj = self.env['fees.structure']
        student_obj = self.env['res.partner']
        st_ids=student_obj.search([('is_parent','=',True)])
        pt_ids=student_obj.search([('is_student','=',True)])
        for student_rec in st_ids:
            student_rec.property_account_customer_advance=678
        for st in pt_ids:
            st.property_account_customer_advance=678

    def get_fee_structure_all(self):
        fee_line_obj = self.env['fees.structure']
        student_obj = self.env['res.partner']

        for student_rec in student_obj.browse(4542):
            fee_lst = []
            fee_lst_detail = []
            for fee_criteria in fee_line_obj.search([
                        ('academic_year_id','=',student_rec.batch_id.id),
                        ('course_id','=',student_rec.course_id.id),
                        ('type','=','academic'),
                    ]):
                for fee_line in fee_criteria.fee_line_ids:
                    if fee_line.fee_pay_type.name != 'one':
                        fee_data = \
                            {
                                'name' : fee_line.name,
                                'amount' : int(fee_line.amount),
                                'type' : fee_line.type,
                                'fee_pay_type' : fee_line.fee_pay_type.id,
                                'sequence': fee_line.sequence,
                                'stud_id' : student_rec.id,
                            }
                        fee_detail={
                        'name' : fee_line.name,
                        'student_id': student_rec.id,
                        'fee_pay_type' : fee_line.fee_pay_type.id,
                        'cal_amount' : 0.00,
                        'rem_amount' : 0.00,
                        'total_amount' : int(fee_line.amount),
                        'discount_amount' : 0.00,
                        }
                        fee_lst.append((0,0,fee_data))
                        fee_lst_detail.append((0,0,fee_detail))
            if len(fee_lst) > 0:
                student_rec.student_fee_line = fee_lst
                student_rec.payble_fee_ids = fee_lst_detail

    @api.multi
    def update_fee_structure(self):

        # first all discount update with 0 value
        for feess in self.student_fee_line:
            feess.discount_amount = 0.0
            feess.discount = 0.0

        if self.discount_on_fee:
            # apply discount on fee structure
            for discount_fee_line in self.discount_on_fee.discount_category_line.search([
                ('discount_category_id','=',self.discount_on_fee.id)]):
                for fees in self.student_fee_line:
                    if fees.name.fees_discount:
                        if fees.name.fees_discount == discount_fee_line.product_id:
                            if discount_fee_line.discount_type == 'amount':
                                if discount_fee_line.discount_amount > 0.00 and fees.amount > 0.00:
                                    fees.discount_amount = discount_fee_line.discount_amount
                                    # fees.discount = (discount_fee_line.discount_amount * 100)/fees.amount
                            elif discount_fee_line.discount_type == 'persentage':
                                if discount_fee_line.discount_persentage > 0.00 and fees.amount > 0.00:
                                    fees.discount = discount_fee_line.discount_persentage

class StudentPayableFee(models.Model):

    _name = 'student.payble.fee'

    @api.depends('total_amount','cal_amount','discount_amount')
    def _remaining_amount_cal(self):
        for rem in self:
            rem.rem_amount = rem.total_amount - (rem.cal_turm_amount+rem.discount_amount)

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

    name = fields.Many2one('product.product','Name')
    month = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    year = fields.Char(string="year", related="month_id.year")
    fee_pay_type = fields.Many2one('fee.payment.type',string="Fee Payment Type")    
    cal_amount = fields.Float("Calculated Amount")
    rem_amount = fields.Float('Remaining Amount',compute='_remaining_amount_cal')
    student_id = fields.Many2one('res.partner',string='Student')
    month_id = fields.Many2one('fee.month','Month Ref',store=True)
    total_amount = fields.Float('Total Amount')
    cal_turm_amount = fields.Float('Paid')
    next_term = fields.Many2one('acd.term',string="Next Term")
    discount_amount = fields.Float(string="Discount Amount")

class StudentFeeStatus(models.Model):

    _name = 'student.fee.status'

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

    month_id = fields.Many2one('fee.month','Month Ref',store=True)
    name = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    year = fields.Char(string="Year", related="month_id.year")
    paid = fields.Boolean('Paid')
    student_id = fields.Many2one('res.partner')
