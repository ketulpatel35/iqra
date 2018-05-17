from openerp import models, fields, api, _
from num2words import num2words
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv
from openerp.tools import float_compare

class account_move_reconcile(models.Model):
    _inherit = "account.move.reconcile"

    def _check_same_partner(self, cr, uid, ids, context=None):
        for reconcile in self.browse(cr, uid, ids, context=context):
            move_lines = []
            if not reconcile.opening_reconciliation:
                if reconcile.line_id:
                    first_partner = reconcile.line_id[0].partner_id.id
                    move_lines = reconcile.line_id

                elif reconcile.line_partial_ids:
                    first_partner = reconcile.line_partial_ids[0].partner_id.id
                    move_lines = reconcile.line_partial_ids

                if any([(line.account_id.type in ('receivable', 'payable') and line.partner_id.id != first_partner) for line in move_lines]):
                    return False
        return True

    # _constraints = [
    #     (_check_same_partner, 'You can only reconcile journal items with the same partner.', ['line_id', 'line_partial_ids']),
    # ]

class Student_Fee_Invoice(models.Model):

    _inherit = 'account.invoice'
    
    @api.multi
    def amount_to_text(self, amount):
        amount_in_text= num2words(amount)
        amount_upper=amount_in_text.upper()
        return amount_upper

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

    batch_id = fields.Many2one('batch',string='Acadamic Year')
    term_id = fields.Many2one('acd.term',string='Term')
    month_id = fields.Many2one('fee.month',string='Month Ref')
    month = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    year = fields.Char(string="Year", related="month_id.year")
    payfort_payment_id = fields.Char(string='PAY ID')
    payfort_pay_date = fields.Date("Payment Date")

    @api.multi
    def confirm_paid(self):
        reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
        if reg_rec.id:
            reg_rec.fee_status = 'academy_fee_pay'
            reg_rec.acd_trx_date = date.today()
        return super(Student_Fee_Invoice, self).confirm_paid()

    @api.multi
    def invoice_validate(self):
        """
        invoice line remaining amount update base on discount.
        ------------------------------------------------------
        :return:
        """
        for invoice_line_rec1 in self.invoice_line:
            for invoice_line_rec2 in self.invoice_line:
                if invoice_line_rec1.product_id.fees_discount.id == invoice_line_rec2.product_id.id:
                    if invoice_line_rec1.rem_amount > 0.00 and invoice_line_rec1.rem_amount >= abs(
                            invoice_line_rec2.rem_amount):
                        invoice_line_rec1.rem_amount -= abs(invoice_line_rec2.rem_amount)
                        invoice_line_rec2.rem_amount = 0.00
        res = super(Student_Fee_Invoice, self).invoice_validate()
        if self.type == "out_invoice" :
            self.bulk_reconciliation()
        return res

class Student_Fee_Invoice_Line(models.Model):

    _inherit = "account.invoice.line"

    parent_id = fields.Many2one('res.partner', string='parent', readonly=True)
    priority = fields.Integer('Priority')
    full_paid = fields.Boolean('Full Paid')
    rem_amount = fields.Float('Remaining Amount')

    @api.model
    def create(self, vals):
        """
        update remaining amount on create invoice line.
        -----------------------------------------------
        :param vals: dictonary
        :return:
        """
        if vals:
            vals['rem_amount'] = vals['price_unit']
        res = super(Student_Fee_Invoice_Line, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """
        update remaining amount on write invoice line unite price.
        ----------------------------------------------------------
        :param vals:dictonary
        :return:
        """
        if 'price_unit' in vals:
            vals['rem_amount'] = vals['price_unit']
        res = super(Student_Fee_Invoice_Line, self).write(vals)
        return res


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    is_parent = fields.Boolean('Is Parent')
    jounral_id_store = fields.Boolean(string='Jounral Store')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    cheque = fields.Boolean(string='Cheque')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')
    invoice_id=fields.Many2one('account.invoice','Invoice')
    parent_email = fields.Char(string='Parent Email')
    parent_mobile = fields.Char(string='Mobile')
    student_class = fields.Many2one('course',string="Class")
    student_section = fields.Many2one('section', 'Section')
    payfort_payment_id = fields.Char(string='PAY ID')
    payfort_pay_date = fields.Date("Payment Date")
    payfort_link_order_id = fields.Char('Payfort Order Id')
    payfort_type = fields.Boolean('For Payfort Payment')
    total_payble_amount = fields.Float()

    @api.multi
    def students_class(self, voucher):
        st_class=''
        if voucher:
            for line in voucher.line_cr_ids:
                if line.move_line_id and line.move_line_id.partner_id:
                   st_class=st_class + (line.move_line_id.partner_id.class_id and line.move_line_id.partner_id.class_id.name or '')+','
        return st_class

    @api.multi
    def childs_name(self, voucher):
        names=''
        if voucher:
            for line in voucher.line_cr_ids:
                if line.move_line_id and line.move_line_id.partner_id:
                   names=names + (line.move_line_id.partner_id.name or '')+','
        return names

    def academic_years(self,parent):
        year=[]
        if parent:
            for child in parent.chield1_ids:
                year.append(child.year_id and child.year_id.name or '')
            year=list(set(year))
            if len (year)>0:
                return year[0]
        return ''       

    @api.v7
    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise except_orm(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise except_orm(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
            'cheque_date':voucher.cheque_start_date,
            'cheque_expiry_date':voucher.cheque_expiry_date,
            'bank_name':voucher.bank_name,
            'cheque':voucher.cheque
        }
        return move

    @api.multi
    # @api.depends('journal_id')
    def onchange_journal(self, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id):
        res = super(AccountVoucher, self).onchange_journal(
            journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id)
        type_rec = self.env['account.journal'].browse(journal_id)
        if res:
            res['value'].update({
                'jounral_id_store': type_rec.is_cheque
            })
        return res

    @api.onchange('cheque_start_date','cheque_expiry_date')
    def cheque_start(self):
        if self.cheque_start_date and self.cheque_expiry_date:
            if self.cheque_start_date > self.cheque_expiry_date:
                raise except_orm(_('Warning!'),
                    _("Start Date must be lower than to Expiry date!"))

    @api.multi
    def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
        student_obj = self.env['res.partner']
        stud_rec = student_obj.browse(partner_id)

        if stud_rec.id and stud_rec.is_parent == True and stud_rec.is_student == False:
            # payment from parent then check parent and it's all child id
            child_lst = []
            child_lst.append(partner_id)
            for student_rec in student_obj.search([('is_parent','=',False),
                                                   ('parents1_id','=',partner_id)]):
                child_lst.append(student_rec.id)
            partner_id = child_lst
            res = super(AccountVoucher, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
            if res:
                res['value']['parent_email'] = stud_rec.parents_email
                res['value']['parent_mobile'] = stud_rec.parent_contact
        elif stud_rec.is_parent == False and stud_rec.is_student == True:
            # payment from child then child id and it's parent id
            child_parent_lst = []
            child_parent_lst.append(partner_id)
            if stud_rec.parents1_id.id:
                child_parent_lst.append(stud_rec.parents1_id.id)
            partner_id = child_parent_lst
            res = super(AccountVoucher, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
            if res:
                res['value']['student_class'] = stud_rec.class_id.id
                res['value']['student_section'] = stud_rec.student_section_id.id
        else:
            res = super(AccountVoucher, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
        total_pay_amount = 0.0
        if 'value' in res:
            if 'line_cr_ids' in res['value'] and res['value']['line_cr_ids']:
                for each in res['value']['line_cr_ids']:
                    if isinstance(each,dict):
                        total_pay_amount += each['amount_unreconciled']
            if 'line_dr_ids' in res['value'] and res['value']['line_dr_ids']:
                for each in res['value']['line_dr_ids']:
                    if isinstance(each,dict):
                        total_pay_amount -= each['amount_unreconciled']
            res['value']['total_payble_amount'] = total_pay_amount
        return res

    @api.multi
    def onchange_amount(self, amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id):
        partner_obj = self.env['res.partner']
        partner_rec = partner_obj.browse(partner_id)
        if partner_rec.is_parent == True and partner_rec.is_student == False:
            # partner payment then parent id and all child id
            child_lst = []
            child_lst.append(partner_id)
            for student_rec in partner_obj.search([('is_parent','=',False),
                                                   ('parents1_id','=',partner_id)]):
                child_lst.append(student_rec.id)
            partner_id = child_lst
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        elif partner_rec.is_parent == False and partner_rec.is_student == True:
            # child payment then child id and its parent id
            child_parent_lst = []
            child_parent_lst.append(partner_id)
            if partner_rec.parents1_id.id:
                child_parent_lst.append(partner_rec.parents1_id.id)
            partner_id = child_parent_lst
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        else:
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        return res

    # @api.multi
    # def recompute_voucher_lines(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     res = super(AccountVoucher, self).recompute_voucher_lines(partner_id, journal_id, amount, currency_id, ttype, date)
    #     student_obj = self.env['res.partner']
    #     total_amount = amount
    #     # advance payment calculation
    #     advance_pay_amount = 0.0
    #     if isinstance(partner_id,list):
    #         for res_value in res:
    #             if res[res_value]['line_dr_ids']:
    #                 for element in res[res_value]['line_dr_ids']:
    #                     if isinstance(element,dict):
    #                         advance_pay_amount += element['amount_unreconciled']
    #
    #     total_amount += advance_pay_amount
    #     if isinstance(partner_id,list):
    #         for partner in partner_id:
    #             if student_obj.browse(partner).is_parent != True:
    #                 for res_value in res:
    #                     if res[res_value]['line_cr_ids']:
    #                         ele_tuple = []
    #                         ele_dict = []
    #                         for element in res[res_value]['line_cr_ids']:
    #                             if isinstance(element,dict):
    #                                 ele_dict.append(element)
    #                             else:
    #                                 ele_tuple.append(element)
    #                         if ele_dict:
    #                             for ele_line in sorted(ele_dict, key=lambda k: k['amount_unreconciled']):
    #                                 if total_amount == 0:
    #                                     ele_line['amount'] = 0
    #                                 else:
    #                                     if ele_line['amount_unreconciled'] > total_amount:
    #                                         ele_line['amount'] = total_amount
    #                                         total_amount = 0
    #                                     else:
    #                                         ele_line['amount'] = ele_line['amount_unreconciled']
    #                                         total_amount -= ele_line['amount_unreconciled']
    #                         line_cr = ele_tuple + ele_dict
    #                         res[res_value]['line_cr_ids'] = line_cr
    #                 return res
    #     return res

    @api.multi
    def action_move_line_create(self):
        res = super(AccountVoucher, self).action_move_line_create()
        invoice_obj = self.env['account.invoice']
        reg_obj = self.env['registration']
        move_ids = []
        amount_alocation = {}
        for voucher_line in self.line_cr_ids:
            move_ids.append(voucher_line.move_line_id.move_id.id)
            amount_alocation.update({voucher_line.move_line_id.move_id.id:voucher_line.amount})

        for invoice_rec in invoice_obj.search([('move_id','in',move_ids)]):
            total_amount = amount_alocation[invoice_rec.move_id.id]
            reg_rec = reg_obj.search([('invoice_id','=',invoice_rec.id)])
            for invoice_line in invoice_rec.invoice_line.search([('invoice_id','=',invoice_rec.id),
                                                                 ('rem_amount','>',0.00)],order='priority desc'):

                if total_amount > 0.00:
                    if total_amount >= invoice_line.rem_amount:
                        # Student fee line Update (full fee paid)
                        fee_line1 = invoice_rec.partner_id.payble_fee_ids.search(
                            [('name', '=', invoice_line.product_id.id),
                             ('student_id', '=', invoice_rec.partner_id.id),
                             ('month_id.batch_id', '=', invoice_rec.batch_id.id)],
                            limit=1)
                        if fee_line1.id:
                            discount_amount = 0.00
                            for discount_fee in invoice_rec.invoice_line.search([('invoice_id', '=', invoice_rec.id)]):
                                if invoice_line.product_id.fees_discount.id == discount_fee.product_id.id:
                                    discount_amount = discount_fee.rem_amount
                                    total_amount -= discount_amount
                                    discount_fee.rem_amount = 0.00

                                fee_line1.cal_turm_amount = fee_line1.cal_turm_amount + invoice_line.rem_amount + discount_amount
                                total_amount -= invoice_line.rem_amount
                                invoice_line.rem_amount = 0.00
                                # update fee status on registration obj
                                if reg_rec.id and reg_rec.fee_status != 'academy_fee_pay':
                                    reg_rec.fee_status = 'academy_fee_partial_pay'

                                # invoice_line.full_paid = True

                                #fee Status
                                fee_status = invoice_rec.partner_id.payment_status.search([('month_id','=',invoice_rec.month_id.id),
                                                                            ('student_id','=',invoice_rec.partner_id.id)],limit=1)
                                if not fee_status.id:
                                    status_val = {
                                        'month_id': invoice_rec.month_id,
                                        'paid': True,
                                    }
                                    invoice_rec.partner_id.payment_status = [(0,0,status_val)]
                                else:
                                    fee_status.paid = True
                            else:
                                total_amount -= invoice_line.rem_amount
                                invoice_line.rem_amount = 0.00
                        else:
                            fee_line2 =  invoice_rec.partner_id.payble_fee_ids.search([('name','=',invoice_line.product_id.id),
                                                                      ('student_id','=',invoice_rec.partner_id.id)],limit=1)
                            if fee_line2.id:
                                fee_line2.cal_turm_amount = fee_line2.cal_turm_amount + total_amount
                                invoice_line.rem_amount -= total_amount
                                total_amount = 0.00
                            else:
                                invoice_line.rem_amount -= total_amount
                                total_amount = 0.00
        return res

    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):

        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, [voucher_id], ['date'], context=context)[0]['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')


        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = line.type =='dr' and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0

            move_rec = move_line_obj.search(cr, uid, [('id', '=', line.move_line_id.id)], context=context)
            move_brw = move_line_obj.browse(cr, uid, move_rec, context=context)

            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': move_brw.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - abs(amount_currency)

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': move_brw.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)

        res = (tot_line, rec_lst_ids)
        return self.post_voucher_move_line(cr, uid, res, voucher_id, context)

    def post_voucher_move_line(self,  cr, uid, res, voucher_id, context=None):
        voucher_obj = self.pool.get('account.voucher')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')

        voucher_rec = voucher_obj.browse(cr, uid, voucher_id, context=context)

        if res and len(res) > 1 and res[1]:
            res_move_id = res[1]
            for each in range(0, len(res_move_id)):
                move_first1_id = account_move_obj.search(cr, uid, [('line_id', '=', res_move_id[each][0])], context=context)
                move_first1_brw = account_move_obj.browse(cr, uid, move_first1_id, context=context)
                if move_first1_brw.id:
                    if voucher_rec.jounral_id_store == 'bank':
                        move_first1_brw.write({'bank_name': voucher_rec.bank_name})
                    if voucher_rec.cheque == True:
                        move_first1_brw.write({'cheque_pay': True,
                                              'cheque_date': voucher_rec.cheque_start_date,
                                              'cheque_expiry_date': voucher_rec.cheque_expiry_date, })
        if voucher_rec.partner_id.is_parent == True:
            if res and len(res) > 1 and res[1]:
                res_move_id = res[1]
                for each in range(0, len(res_move_id)):
                    move_first_id = account_move_obj.search(cr, uid, [('line_id', '=', res_move_id[each][1])], context=context)
                    move_first_brw = account_move_obj.browse(cr, uid, move_first_id, context=context)
                    if move_first_brw.id:
                        account_move_line_rec = account_move_line_obj.browse(cr, uid, res_move_id[each][0], context=context)
                        parent_id = account_move_line_rec.partner_id.id
                        account_move_line_rec.write({'partner_id': move_first_brw.partner_id.id})
        return res


class Account_Invoice_Line(models.Model):

    _inherit = 'account.move.line'

    parents1_id = fields.Many2one('res.partner', 'Parent')
