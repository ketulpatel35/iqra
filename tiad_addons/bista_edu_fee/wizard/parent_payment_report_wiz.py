from openerp import models, fields, api, _
from datetime import datetime, timedelta
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning

class parent_payment_report_wiz(models.TransientModel):
    _name='parent.payment.report.wiz'
    
    parent_id = fields.Many2one('res.partner',string="Parent Name" )
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(sring="Date To")
    invoice_ids = fields.Many2many('account.invoice',string="Invoices")
    date_today = fields.Date(string="Todays Date")
    past_balance = fields.Float(string="Past balance")
    user = fields.Many2one('res.users',string="Current User")
#    running_balance_credit=fields.Float(string="Running balance after all creadit lines")
    
    current_running_balance=fields.Float(string="Current Running balance")
    _defaults={
    'current_running_balance':0.0
    
    
    }

    @api.multi
    def calc_current_running_balance(self,total,paid):
        self.current_running_balance=self.current_running_balance+total-paid
        return self.current_running_balance

    @api.multi
    def open_report(self):
        invoice_ids=[]
       
        for each1 in self.parent_id.chield1_ids.ids:
            invoices=self.env['account.invoice'].search([('partner_id','=',each1),('state','in',['open','paid']),('date_invoice','>=',self.date_from),('date_invoice','<=',self.date_to)])
            for each in invoices:
                invoice_ids.append(each.id)

        past_balance=0.0
        for each1 in self.parent_id.chield1_ids.ids:
              invoices_past=self.env['account.invoice'].search([('partner_id','=',each1),('state','in',['open','paid']),('date_invoice','<',self.date_from)])  
              for each in invoices_past:
                    past_balance=past_balance+each.residual

        self.user=self._uid               
        self.past_balance=past_balance
        self.invoice_ids=[(6,0,invoice_ids)]
        self.date_today = date.today()
        
#        running_bal=0+self.past_balance
#        for each in self.invoice_ids:
#            for line in each.invoice_line:
#                running_bal=running_bal+line.price_subtotal
#           
#        self.running_balance_credit=running_bal   
      
        value = {
            'type': 'ir.actions.report.xml',
            'report_name': 'bista_edu_fee.report_parent_payment',
            'datas': {
                'model': 'parent.payment.report.wiz',
                'id': self.id,
                'ids': [self.id],
                'report_type': 'pdf',
                'report_file': 'bista_edu_fee.report_parent_payment'
            },
            'nodestroy': True
        }
        return value