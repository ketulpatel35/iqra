# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from openerp import _
from openerp import api
from openerp import fields
from openerp import models
from openerp.exceptions import RedirectWarning
from openerp.exceptions import Warning
from openerp.exceptions import except_orm


class promote_student(models.Model):
    _name = "promote.student"

    name = fields.Char(default='Student')
    class_id = fields.Many2one('course', string="Class")
    batch_id = fields.Many2one('batch', string="Academic Year")
    section_ids = fields.Many2many('section', string='Section')
    promote_to_class = fields.Many2one('course', string="Promote To Class")
    promote_to_batch = fields.Many2one('batch', string="Promote To Academic Year")
    promote_to_section = fields.Many2one('section', string='Promote To Section')
    student_line = fields.One2many('promote.student.line', 'promote_student_id', 'Promote Student')
    state = fields.Selection([('draft', 'Draft'), ('promote', 'Promoted')], string='State', default='draft')

    @api.onchange('promote_to_class')
    def onchange_promote_class(self):
        if self.promote_to_class:
            if (self.class_id.code == 'KG1' and self.promote_to_class.code == 'KG1') \
                    or (self.class_id.code == 'KG2' and (self.promote_to_class.code == 'KG1' or self.promote_to_class.code == 'KG2')) \
                    or (self.class_id.code != 'KG1' and self.class_id.code != 'KG2' and self.class_id.code >= 1 and (self.promote_to_class.code == 'KG1' or self.promote_to_class.code == 'KG2')) \
                    or (self.class_id.code != 'KG1' and self.class_id.code != 'KG2' and self.class_id.code >= 1 and self.promote_to_class.code >= 1 and (self.promote_to_class.code <= self.class_id.code)):
                raise except_orm(_('Warning!'),
                    _("promote to class can not be eqal to or lower than current class %s!")%self.class_id.name)  

    @api.onchange('promote_to_batch')
    def onchange_promote_batch(self):
        if self.promote_to_batch:
            if self.batch_id.end_date > self.promote_to_batch.start_date:
                raise except_orm(_('Warning!'),
                        _("Promoted academic year can not be equal to or less than current academic year!"))
            
    @api.multi
    def student_promotion(self):
        """
            this method used to promote student to the next class
            and to update the fee structure accordingly.
            
        """
        student_obj = self.env['res.partner']
        fees_obj = self.env['fees.structure']
        promote_obj = self.env['promote.student.line']
        fees_data = fees_obj.search([('type', '=', 'academic'), ('course_id', '=', self.promote_to_class.id), ('academic_year_id', '=', self.promote_to_batch.id)])
        student_data = student_obj.search([('is_student', '=', True), ('promoted', '=', False), ('course_id', '=', self.class_id.id), ('batch_id', '=', self.batch_id.id), ('section_id', 'in', self.section_ids.ids)])
        print student_data
        if len(student_data)>0:
            self.state = 'promote'
        fee_lst = []
        
        for student in student_data:
            print student
            lines = {
                'promote_student_id': self.ids[0],
                'student_id': student.id,
                'current_acad_year':student.batch_id.name,
                'current_acad_class': student.course_id.name,
                'current_acad_section': student.section_id.name,
                'new_acad_year': self.promote_to_batch.id,
                'new_acad_class': self.promote_to_class.id,
                'new_acad_section': self.promote_to_section.id
                }
            promote_obj.create(lines)
            student.course_id = self.promote_to_class
            student.class_id = self.promote_to_class
            student.batch_id = self.promote_to_batch
            student.year_id = self.promote_to_batch
            student.section_id = self.promote_to_section
            student.promoted = True
            student.discount_on_fee = False

            for fee in student.student_fee_line:
#                fee.student_history_id = False   //if we want to delete previous history
                fee.student_history_id = fee.stud_id.id
                fee.stud_id = False

            for fees in fees_data.fee_line_ids:
                fees_lines = {
                    'stud_id':student.id,
                    'sequence':fees.sequence,
                    'name':fees.name,
                    'amount':int(fees.amount),
                    'type':fees.type,
                    'fee_pay_type':fees.fee_pay_type.id
                    }
                fee_lst.append((0, 0, fees_lines))
            student.student_fee_line = fee_lst
            fee_lst = []

class promote_student_line(models.Model):
    _name = "promote.student.line"
    
    student_id = fields.Many2one('res.partner', 'Student')
    current_acad_year = fields.Char('Current Academic Year')
    current_acad_class = fields.Char('Current Class')
    current_acad_section = fields.Char('Current Section')
    new_acad_year = fields.Many2one('batch', 'New Academic Year')
    new_acad_class = fields.Many2one('course', 'New Class')
    new_acad_section = fields.Many2one('section', 'New Section')
    promote_student_id = fields.Many2one('promote.student', 'Student Reference')
    
class student_promotion(models.Model):
    _inherit = 'res.partner'
    
    promoted = fields.Boolean(string='Promoted')
    student_fee_history = fields.One2many('fees.line','student_history_id','Fee History')
    promoted_fee_structure_confirm = fields.Boolean('Fee Structure Confirm')
    promoted_fee_structure_done = fields.Boolean('Fee Structure Done')
    
    @api.multi
    def send_mail_for_promoted_fee_structure(self):
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('bista_promotion', 'email_template1_promote_fee_structure')[1]
        template_rec = self.env['email.template'].browse(template_id)
        template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id)
            
    @api.multi
    def confirm_promoted_fee_structure(self):
        if self.promoted_fee_structure_done == True:
            raise except_orm(_('Warning!'),_("Fee structure Already confirm."))
        else:
            if self.discount_on_fee.id:
                self.discount_on_fee = self.discount_on_fee.id
                self.update_fee_structure()
            self.promoted_fee_structure_done = True
    
    @api.multi
    def reverse_promoted_fee_structure(self):
        if self.promoted_fee_structure_done == False:
            raise except_orm(_('Warning!'),_("Fee structure Already Reversed."))
        else:
            fee_line_obj = self.env['fees.structure']
            for fees in fee_line_obj.search([
                    ('academic_year_id','=',self.batch_id.id),
                    ('course_id','=',self.course_id.id),
                    ('type','=','academic')]):
                for fee_line in fees.fee_line_ids:
                    for stud_fee in self.student_fee_line:
                        if stud_fee.name == fee_line.name:
                            stud_fee.write({'amount':fee_line.amount,
                                                'update_amount':0.00})
            self.promoted_fee_structure_done = False
            
    @api.multi
    def confirm_done_promoted_fee_structure(self):
        self.promoted_fee_structure_confirm = True
        self.send_mail_for_promoted_fee_structure()