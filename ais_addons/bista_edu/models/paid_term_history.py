from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class paid_term_history(models.Model):

    _name = 'paid.term.history'
    
    batch_id=fields.Many2one('batch',string="Academic Year")
    term_id=fields.Many2one('acd.term',strings="Term")
    student_id = fields.Many2one('res.partner',string='student')