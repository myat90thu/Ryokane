# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


# Add analytic tags in sale order lines from sale order form view


# class AccountMove(models.Model):
#     _inherit = 'account.move'


class OrderLine(models.Model):
    _inherit = 'sale.order'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.onchange('analytic_tag_ids')
    def onchange_tag(self):
        for order in self.order_line:
            order.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })


# Add analytic account in invoice lines from invoice form view


# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#     @api.model
#     def create(self, vals):
#         res = super(AccountInvoiceLine, self).create(vals)
#         for x in res:
#             x.update({
#                 'analytic_tag_ids': res.invoice_id.analytic_tag_id,
#             })
#         return res


class InvoiceLines(models.Model):
    _inherit = 'account.invoice'

    # analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.model
    def create(self, vals):
        res = super(InvoiceLines, self).create(vals)
        for x in res.tax_line_ids:
            x.update({
                'analytic_tag_ids': res.analytic_tag_id,
            })

        for x in res.invoice_line_ids:
            x.update({
                'analytic_tag_ids': res.analytic_tag_id,
            })
        return res

    @api.onchange('analytic_account_id')
    def onchange_account(self):
        for lines in self.invoice_line_ids:
            lines.update({
                'account_analytic_id': self.analytic_account_id.id
            })

    @api.onchange('analytic_tag_id')
    def onchange_account(self):
        for lines in self.invoice_line_ids:
            lines.update({
                'analytic_tag_ids': self.analytic_tag_id
            })
        for tax_line in self.tax_line_ids:
            tax_line.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_id.ids)],
                'account_analytic_id': self.account_analytic_id.id
            })

    @api.onchange('tax_line_ids')
    def onchange_tax_tags(self):
        for tax_line in self.tax_line_ids:
            tax_line.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_id.ids)],
                'account_analytic_id': self.account_analytic_id.id
            })


# Add analytic account in invoice lines from invoice form view


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('analytic_tag_ids')
    def onchange_purchase_tag(self):
        for lines in self.order_line:
            lines.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })

    @api.onchange('analytic_account_id')
    def onchange_purchase_analytic_account(self):
        for lines in self.order_line:
            lines.update({
                'account_analytic_id': self.analytic_account_id.id
            })


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def action_post(self):
        res = super(AccountMove, self).action_post()

        dimension_tags_allowed = []
        for line in self.line_ids:
            tag_ids = line.analytic_tag_ids.ids
            for dimension in line.account_id.analytic_dimension_ids:
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
                        raise ValidationError(_("Please choose a valid Tag for dimension: %s  and account: %s") % (
                        dimension.analytic_dimension_id.name, line.account_id.code))
            allowed_tag_val = []
            for tag in tag_ids:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            line.update({
                'analytic_tag_ids': [(6, 0, allowed_tag_val)]
            })
            if not line.analytic_tag_ids:
                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
        return res


class JournalEntry(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id')
    def onchange_journal(self):
        tags = []
        invoice = self.journal_id.default_debit_account_id.analytic_dimension_ids
        for tag in invoice:
            if tag.default_value:
                tags.append(tag.default_value.id)
        self.update({
            'analytic_tag_ids': tags
        })
        dest_account = self.destination_account_id.analytic_dimension_ids
        tag_vals = []
        for tag in dest_account:
            if tag.default_value:
                tag_vals.append(tag.default_value.id)
        self.update({
            'partner_analytic_tags': tag_vals
        })

        dimensions = [val.analytic_dimension_id.id for val in invoice]
        return {'domain': {
            'analytic_tag_ids': [('analytic_dimension_id', 'in', dimensions)],
        }}

    @api.onchange('journal_id')
    def onchange_journal_partner(self):
        dest_account = self.destination_account_id.analytic_dimension_ids
        dimensions = [val.analytic_dimension_id.id for val in dest_account]
        return {'domain': {
            'partner_analytic_tags': [('analytic_dimension_id', 'in', dimensions)],
        }}

    @api.multi
    def action_validate_invoice_payment(self):
        tags = self.analytic_tag_ids.ids
        for tag_val in self.journal_id.default_debit_account_id.analytic_dimension_ids:
            dimension_tags = tag_val.analytic_dimension_id.analytic_tag_ids.ids
            occurance = False
            for x in set(dimension_tags):
                if tags.count(x) > 0:
                    occurance = True
            if occurance is False:
                if tag_val.default_value:
                    tags.append(tag_val.default_value.id)
                else:
                    raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
        dimension_ids = []
        for val in self.analytic_tag_ids:
            dimension_ids.append(val.analytic_dimension_id.id)
        if len(set(dimension_ids)) != len(dimension_ids):
            raise ValidationError(_("You cannot set two tags from same dimension."))
        partner_tags = self.partner_analytic_tags.ids
        for tag_val in self.destination_account_id.analytic_dimension_ids:
            dimension_tags = tag_val.analytic_dimension_id.analytic_tag_ids.ids
            occurance = False
            for x in set(dimension_tags):
                if partner_tags.count(x) > 0:
                    occurance = True
            if occurance is False:
                if tag_val.default_value:
                    partner_tags.append(tag_val.default_value.id)
                else:
                    raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
        self.partner_analytic_tags = partner_tags
        dimension_ids = []
        for val in self.partner_analytic_tags:
            dimension_ids.append(val.analytic_dimension_id.id)
        if len(set(dimension_ids)) != len(dimension_ids):
            raise ValidationError(_("You cannot set two tags from same dimension."))
        res = super(JournalEntry, self).action_validate_invoice_payment()
        return res

    @api.multi
    def _get_liquidity_move_line_vals(self, amount):
        res = super(JournalEntry, self)._get_liquidity_move_line_vals(amount)
        res.update({
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
        })
        return res

    @api.multi
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        counterpart_aml.update({
            'analytic_tag_ids': self.partner_analytic_tags.ids
        })
        # Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
                date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id,
                                                               self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        # Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        # validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        # reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)
        return move
