from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    analytic_tag_id = fields.Many2many('account.analytic.tag', String='Partner Analytic Tag')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', store=True, string='Analytic Account')

    @api.multi
    def action_invoice_open(self):
        dimension_tags_allowed = []
        for invoice_ids in self.invoice_line_ids:
            tag_ids = invoice_ids.analytic_tag_ids.ids
            for dimension in invoice_ids.account_id.analytic_dimension_ids:
                dimension_tags = dimension.analytic_dimension_id.analytic_tag_ids.ids
                dimension_tags_allowed += dimension_tags
                occurance = False
                for x in set(dimension_tags):
                    if tag_ids.count(x) > 0:
                        occurance = True
                if occurance is False:
                    if dimension.default_value:
                        tag_ids.append(dimension.default_value.id)
                    elif invoice_ids.display_type == 'line_section':
                        pass
                    else:
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))

            allowed_tag_val = []
            for tag in tag_ids:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            invoice_ids.update({
                'analytic_tag_ids': [(6, 0, allowed_tag_val)]
            })
            if not invoice_ids.analytic_tag_ids and invoice_ids.display_type != 'line_section':
                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))

        tag_vals = self.analytic_tag_id.ids
        if self:
            dimension_tags_allowed = []
            for dimension in self.account_id.analytic_dimension_ids:
                dimension_tags = dimension.analytic_dimension_id.analytic_tag_ids.ids
                dimension_tags_allowed += dimension_tags
                occurance = False
                for x in set(dimension_tags):
                    if tag_vals.count(x) > 0:
                        occurance = True
                if occurance is False:
                    if dimension.default_value:
                        tag_vals.append(dimension.default_value.id)
                    elif invoice_ids.display_type == 'line_section':
                        pass
                    else:
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
            allowed_tag_val = []
            for tag in tag_vals:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            self.update({
                'analytic_tag_id': [(6, 0, allowed_tag_val)]
            })
            if not self.analytic_tag_id and invoice_ids.display_type != 'line_section':
                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))

        for tax_ids in self.tax_line_ids:
            dimension_tags_allowed = []
            tag_ids = tax_ids.analytic_tag_ids.ids
            for dimension in tax_ids.account_id.analytic_dimension_ids:
                dimension_tags = dimension.analytic_dimension_id.analytic_tag_ids.ids
                dimension_tags_allowed += dimension_tags
                occurance = False
                for x in set(dimension_tags):
                    if tag_ids.count(x) > 0:
                        occurance = True
                if occurance is False:
                    if dimension.default_value:
                        tag_ids.append(dimension.default_value.id)
                    else:
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
            allowed_tag_val = []
            for tag in tag_ids:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            tax_ids.update({
                'analytic_tag_ids': [(6, 0, allowed_tag_val)]
            })
            if not tax_ids.analytic_tag_ids:
                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
            dimension_ids = []
            for val in tax_ids.analytic_tag_ids:
                dimension_ids.append(val.analytic_dimension_id.id)
            if len(set(dimension_ids)) != len(dimension_ids):
                raise ValidationError(_("You cannot set two tags from same dimension."))

        res = super(AccountInvoice, self).action_invoice_open()
        return res

    @api.model
    def create(self, vals):
        if vals.get('analytic_tag_ids'):
            vals.update({
                'analytic_tag_id': vals['analytic_tag_ids']
            })
        res = super(AccountInvoice, self).create(vals)
        return res

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
