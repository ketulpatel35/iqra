from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class MinistryApprovalConfirm(models.TransientModel):
    _name = 'ministry.approval.confirm'

    @api.multi
    def ministry_confirm(self):
        active_ids = self._context['active_ids']
        trans_obj = self.env['trensfer.certificate']
        for trans_rec in trans_obj.browse(active_ids):
            if trans_rec.state != 'mini_app':
                raise except_orm(_('Warning!'),
                    _(" You can confirm the TC application for '%s' in 'Ministry Approval Awaited' state!")%
                            trans_rec.name.name)
            trans_rec.ministry_approval_confirm()
