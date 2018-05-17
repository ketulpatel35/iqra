# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class pdc_detail(models.Model):
    _name='pdc.detail'
    _order = "cheque_start_date"
    
    name=fields.Char('Cheque Number',required=True)
    period_id = fields.Many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]})
    state=fields.Selection(
            [('draft','Draft'),
             ('posted','Posted'),
             ('cleared','Cleared'),
             ('bounced','Bounced'),
             ('cancel','Cancelled'),
            ],'Status', readonly=True, default='draft', track_visibility='onchange', copy=False,)
    journal_id=fields.Many2one('account.journal', 'Journal', readonly=True,)
    chk_fee_type=fields.Selection([('reg', 'Registration Fee Cheque'), ('academic', 'Academic Fee Cheque')], 'Fee Cheque Type')
    journal_entry_id=fields.Many2one('account.move', 'Registration Fee Journal', readonly=True,)
    voucher_id=fields.Many2one('account.voucher', 'Payment', readonly=True,)
    cheque_start_date = fields.Date('Cheque Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    party_name = fields.Char('Party Name')
    amount= fields.Float('Cheque Amount', digits_compute=dp.get_precision('Account'), readonly=True)
    reason = fields.Char(string="Cheque Bounce Reason",size=126)
    cleared_entry_id=fields.Many2one('account.move', 'Cleared Journal Entry', readonly=True,)
    enquiry_no = fields.Char(sring='Enquiry Form No', readonly='1')
    partner_id=fields.Many2one('res.partner', 'Customer', readonly=True,)
    
    @api.multi
    def bounce_cheque_wiz(self):
        
        view = self.env.ref('pdc_detail.bounce_reason_wiz_view')
        return {
            'name': _('Cheque Bounce'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bounce.reason.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }
    
    @api.multi
    def post_cheque(self):
        for chk in self:
            print'chk=========', chk
            if chk.chk_fee_type=='reg':
                if chk.journal_entry_id and chk.journal_entry_id.id:
                    chk.journal_entry_id.button_validate()
                    chk.state='posted'
            elif chk.chk_fee_type=='academic':
                if not chk.voucher_id:
                    raise except_orm(_('Warning!'),
                        _("No payment linked with this Check"))
                chk.voucher_id.move_id.button_validate()
                chk.state='posted'
            else:
                if chk.journal_entry_id and chk.journal_entry_id.id:
                    chk.journal_entry_id.button_validate()
                    chk.state='posted'
        return True
                
                    
    @api.multi
    def cleared_cheque(self):
        account_move_obj = self.env['account.move']
        jounral_dict1 = {}
        jounral_dict2 = {}
        partner_id=False
        for chk in self:
            partner_id=False
            if chk.chk_fee_type=='reg' and chk.journal_entry_id.state != 'posted':
                raise except_orm(_('Warning!'),
                    _("Cheque's journal entry is not posted.You can not clear this cheque"))
            if chk.chk_fee_type=='academic':  
                if chk.voucher_id and chk.voucher_id.move_id and chk.voucher_id.move_id.state!= 'posted':
                    raise except_orm(_('Warning!'),
                    _("Cheque's payment journal entry is not posted.You can not clear this cheque"))
                if chk.voucher_id.move_ids:
                    partner_id= chk.voucher_id.move_ids[0].partner_id.id  
                print'partner_id============================',partner_id
            journal=self.env['account.journal'].search([('name','=','Bank')], limit=1)
            if not journal.id:
                raise except_orm(_('Warning!'),
                    _("Bank Journal is not found."))
            
            jounral_dict1.update({'name':chk.name,'debit':chk.amount,'partner_id':partner_id})
            jounral_dict2.update({'name':chk.name,'credit':chk.amount,'account_id':chk.journal_id.default_credit_account_id.id,'partner_id':partner_id})

            jounral_data = {'journal_id':journal.id,
                            'line_id':[(0,0,jounral_dict1),(0,0,jounral_dict2)],
                            'ref':'['+chk.name or '' + ']' + chk.party_name or '',
                            'bank_name':chk.bank_name,
                            'cheque_date':chk.cheque_start_date,
                            'cheque_expiry_date':chk.cheque_expiry_date,
                            
                            }  
            bank_jounral = account_move_obj.create(jounral_data)
            bank_jounral.button_validate()
            chk.state='cleared'
            chk.cleared_entry_id=bank_jounral.id
        return True
