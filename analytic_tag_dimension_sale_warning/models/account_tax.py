from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class AnalyticAccountEntry(models.Model):
    _inherit = 'account.invoice'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        store=True, string='Analytic Account')

    @api.multi
    def action_move_create(self):
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)
            name = inv.name or ''
            if inv.payment_term_id:
                totlines = \
                inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id,
                                                                    inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'account_analytic_id': inv.account_analytic_id.id,
                        'analytic_tag_id': inv.analytic_tag_id.ids,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'account_analytic_id': inv.account_analytic_id.id,
                    'analytic_tag_id': inv.analytic_tag_id.ids,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice=inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True

# Add tag in list view


class AnalyticTagList(models.Model):
    _inherit = 'account.analytic.line'

    tag_ids = fields.Many2many(String='Analytic Tag')

# function to create positive value to debit account in sale


class AccountAnalyticLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    def _prepare_analytic_line(self):
        if self.invoice_id.type == 'out_invoice' or self.invoice_id.type == 'out_refund':
            amount = (self.debit or 0.0) - (self.credit or 0.0)
            default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
            return {
                'name': default_name,
                'date': self.date,
                'account_id': self.analytic_account_id.id,
                'tag_ids': [(6, 0, self._get_analytic_tag_ids())],
                'unit_amount': self.quantity,
                'product_id': self.product_id and self.product_id.id or False,
                'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
                'amount': amount,
                'general_account_id': self.account_id.id,
                'ref': self.ref,
                'move_id': self.id,
                'user_id': self.invoice_id.user_id.id or self._uid,
                'partner_id': self.partner_id.id,
                'company_id': self.analytic_account_id.company_id.id or self.env.user.company_id.id,
            }

        if self.invoice_id.type == 'in_invoice' or self.invoice_id.type == 'in_refund':
            amount = (self.debit or 0.0) - (self.credit or 0.0)
            default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
            return {
                'name': default_name,
                'date': self.date,
                'account_id': self.analytic_account_id.id,
                'tag_ids': [(6, 0, self._get_analytic_tag_ids())],
                'unit_amount': self.quantity,
                'product_id': self.product_id and self.product_id.id or False,
                'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
                'amount': amount,
                'general_account_id': self.account_id.id,
                'ref': self.ref,
                'move_id': self.id,
                'user_id': self.invoice_id.user_id.id or self._uid,
                'partner_id': self.partner_id.id,
                'company_id': self.analytic_account_id.company_id.id or self.env.user.company_id.id,
            }
        res = super(AccountAnalyticLine, self)._prepare_analytic_line()
        return res