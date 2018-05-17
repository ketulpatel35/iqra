from openerp import models, fields, api, _

class NextYearAdvanceFee(models.Model):

    _name = 'next.year.advance.fee'

    @api.depends('next_year_advance_fee_line_ids')
    def _get_total_amount(self):
        for rec in self:
            t_amount = 0.00
            for fee_line_id in rec.next_year_advance_fee_line_ids:
                t_amount += fee_line_id.amount
            rec.total_amount = t_amount

    @api.one
    @api.depends('total_amount','total_paid_amount')
    def _get_residual_amount(self):
        for rec in self:
            rec.residual = rec.total_amount - self.total_paid_amount

    partner_id = fields.Many2one('res.partner',string='Student')
    reg_id = fields.Many2one('registration',string ='Registration ID')
    enq_date = fields.Date('Enquiry Date')
    order_id = fields.Char(string='Order Id')
    batch_id = fields.Many2one('batch', 'Academic Year',required=True)
    state = fields.Selection([('fee_unpaid', 'Un paid'), ('fee_partial_paid', 'Partial Paid'),
                              ('fee_paid', 'Fee Paid'),('invoice_reconcile','Invoiced & Reconcile')],
                             select=True, string='Stage',default='fee_unpaid')
    next_year_advance_fee_line_ids = fields.One2many('next.year.advance.fee.line','next_year_advance_fee_id',
                                                     string='Fee Line')
    total_amount = fields.Float('Total Amount', compute='_get_total_amount')
    residual = fields.Float('residual', compute='_get_residual_amount', readonly='1')
    total_paid_amount = fields.Float('Total Paid Amount')
    payment_ids = fields.Many2many('account.voucher','next_year_advance_payment','next_year_adv_fee','voucher_ids')
    journal_ids = fields.Many2many('account.journal','next_year_journal','next_year_id','journal_id')
    journal_id = fields.Many2one('account.journal')

    @api.multi
    def create(self,vals):
        order_id = self.env['ir.sequence'].get('next.year.adv.fee') or '/'
        vals['order_id'] = order_id
        return super(NextYearAdvanceFee, self).create(vals)

class NextYearAdvanceFeeLine(models.Model):

    _name = 'next.year.advance.fee.line'

    name = fields.Many2one('product.product',string='Name')
    description  = fields.Char('Description ')
    account_id = fields.Many2one('account.account',string='Account')
    next_year_advance_fee_id = fields.Many2one('next.year.advance.fee',string='Next Year Advance Fee')
    priority = fields.Integer('Priority')
    amount = fields.Float('Amount')
    rem_amount = fields.Float('Remaining Amount')
