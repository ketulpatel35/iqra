from openerp import models, fields, api, _

class reject_reason_wiz(models.Model):

    _name='reject.reason.wiz'
    
    reason = fields.Char(string="Please mention reason to reject this record",size=126)
    
    @api.multi
    def reject_state(self):
        active_id=self._context['active_id']
        reg_obj=self.env['registration'].browse(active_id)
        
        if reg_obj.state == 'awaiting_fee':
            reg_obj.student_id.active=False

        if reg_obj.state == 'pending':
            reg_obj.state_dropdown = reg_obj.state
	    reg_obj.decision_reject_state()
        else:
            reg_obj.write({'state_hide_ids':[(0,0, {'reg_id': reg_obj.id,'state_name':reg_obj.state})],
                           'state_hide':reg_obj.state})
            reg_obj.state_dropdown = reg_obj.state
            reg_obj.state_dropdown = reg_obj.state
	    reg_obj.state = 'rejected'
        reg_obj.reject_reason=self.reason
