from openerp import models, fields, api, _
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    @api.multi
    def proforma_voucher(self):
        self.action_move_line_create()
        pdc_obj = self.env['pdc.detail']
        

        for voucher in self:
            print'jkjkjkjkjkjjkjkjk==============',voucher.chk_num,
            if voucher.journal_id.is_cheque:
                vals={
                    'name':voucher.chk_num,
                    'amount':voucher.amount,
                    'journal_id':voucher.journal_id and voucher.journal_id.id or False,
                    'cheque_start_date':voucher.cheque_start_date,
                    'cheque_expiry_date':voucher.cheque_expiry_date,
                    'bank_name':voucher.bank_name,
                    'party_name':voucher.party_name,
                    'period_id':voucher.period_id and voucher.period_id.id or False ,
                    'state':'draft',
                    'chk_fee_type':'academic',
                    'voucher_id':voucher.id,
                    'partner_id':voucher.partner_id.id

                        }
                pdc=pdc_obj.create(vals)
                print 'pdc=========================',pdc
        return True
