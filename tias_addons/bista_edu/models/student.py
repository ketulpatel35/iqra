# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date,datetime


class Student(models.Model):

    _inherit = 'res.partner'

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
    category_id = fields.Many2one('category', string='Category')
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
    section_id = fields.Many2one('section', 'Admitted section')
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
    sibling_ids = fields.One2many('sibling','student_id',string='Sibling')
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

    _defaults={
     'student_id':lambda s, cr, uid, c: s.pool.get('ir.sequence').get(cr,uid,'res.partner'),
    }

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            _name = ''
            if record.is_parent == True:
                _name = '[ ' + str(record.parent1_id) + ' ]' + str(record.name)
            elif record.is_student == True:
                _name = '[ ' + str(record.student_id) + ' ]' + str(record.name)
            else:
                _name = str(record.name)
            res.append((record.id,_name))
        return res

    @api.multi

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
