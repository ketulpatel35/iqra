# -*- coding: utf-8 -*-
from datetime import datetime
import datetime as d
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class Batch(models.Model):

    _name = 'batch'

    @api.multi
    def compute_current_year(self):
        """
        this method is use to make current academic year
        base on current date.
        -----------------------------------------
        :return :
        """
        for record in self:
            s_date = datetime.strptime(record.start_date,"%Y-%m-%d").date()
            e_date = datetime.strptime(record.end_date,"%Y-%m-%d").date()
            c_date = d.date.today()
            if s_date <= c_date <= e_date:
                record.current_academic = True
            else:
                record.current_academic = False

    code= fields.Char(size=8, string='Code', required=True)
    name= fields.Char(size=32, string='Name', required=True)
    start_date= fields.Date(string='Start Date', required=True)
    end_date= fields.Date(string='End Date', required=True)
    course_ids = fields.Many2many('course','batch_name','course_name',string="Classes")
    month_ids = fields.One2many('fee.month','batch_id',string='Month')
    effective_date = fields.Date(string="Effective Date")
    term_ids = fields.One2many('acd.term','batch_id',string="Academic Terms")
    current_academic = fields.Boolean('Current Academic Year',compute='compute_current_year')
    advance_payment_reconcile_date = fields.Date('Advance Payment Reconcile Date')

    @api.model
    def create(self,vals):
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        if len(prev_records)!=0:
            raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).create(vals)

    @api.multi
    def write(self,vals):
        if 'start_date' not in vals:
            vals['start_date']=self.start_date
        if 'end_date' not in vals:
            vals['end_date']=self.end_date
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        for each in prev_records:
            if each.id != self.id:
                raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).write(vals)

    @api.model
    def create(self,vals):
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        if len(prev_records)!=0:
            raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).create(vals)

    @api.multi
    def write(self,vals):
        if 'start_date' not in vals:
            vals['start_date']=self.start_date
        if 'end_date' not in vals:
            vals['end_date']=self.end_date
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        for each in prev_records:
            if each.id != self.id:
                raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).write(vals)

    @api.onchange('start_date','end_date')
    def _compute_month_of_batch(self):
        """
        this method used to compute how many months,
        comes in between start date and end date.
        ------------------------------------------
        @param self : object pointer
        @worning : if start date greter then end date
        """
        if self.start_date and self.end_date:
            st_date = datetime.strptime(self.start_date , '%Y-%m-%d')
            en_date = datetime.strptime(self.end_date , '%Y-%m-%d')
            if st_date < en_date:
                if self.month_ids:
                    for delet_month in self.month_ids:
                        self.month_ids = ([(2,delet_month.id)])
                s_month = int(self.start_date.split('-')[1])
                e_month = int(self.end_date.split('-')[1])
                s_year = int(self.start_date.split('-')[0])
                e_year = int(self.end_date.split('-')[0])
                s_date = datetime.strptime(self.start_date,"%Y-%m-%d").date()
                e_date = datetime.strptime(self.end_date,"%Y-%m-%d").date()
                month_diff = self.env['registration'].get_person_age(s_date,e_date)
                total_month = month_diff.get('months')
                if month_diff.get('days') > 15:
                    total_month += 1
                if total_month % 2 == 0:
                    qter_month = total_month / 2
                else:
                    total_month += 1
                    qter_month = total_month / 2
                month_lst = []
                code = 1
                while -1:
                    if code in [1,qter_month+1]:
                        qtr = True
                    else:
                        qtr = False
                    if code % 2 == 0:
                        alt = False
                    else:
                        alt = True
                    if code % 3 == 1:
                        qtr_month = True
                    else:
                        qtr_month = False
                    if s_month == e_month and s_year == e_year:
                        month_lst.append((0,0,{
                            'code': code,
                            'name': s_month,
                            'year': s_year,
                            'alt_month': alt,
                            'quater_month': qtr,
                            'qtr_month': qtr_month,
                            }))
                        break
                    if s_month == 13:
                        s_month = 1
                        s_year += 1
                    else:
                        month_lst.append((0,0,{
                            'code': code,
                            'name': s_month,
                            'year': s_year,
                            'alt_month': alt,
                            'quater_month': qtr,
                            'qtr_month': qtr_month,
                            }))
                        code += 1
                        s_month += 1
                self.month_ids = month_lst
            else:
                raise except_orm(_('Warning!'),
                    _("end date should be greater than start date !"))