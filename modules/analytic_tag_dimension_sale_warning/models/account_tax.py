from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


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