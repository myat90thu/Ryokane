from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        for x in res.tax_line_ids:
            x.update({
                'analytic_tag_ids': res.analytic_tag_id,
            })
        # for x in res.invoice_line_ids:
        #     x.update({
        #         'analytic_tag_ids': res.analytic_tag_id,
        #     })
        return res

    @api.onchange('analytic_account_id')
    def onchange_account(self):
        for lines in self.invoice_line_ids:
            lines.update({
                'account_analytic_id': self.analytic_account_id.id
            })

    # @api.onchange('analytic_tag_id')
    # def onchange_account(self):
    #     for lines in self.invoice_line_ids:
    #         lines.update({
    #             'analytic_tag_ids': self.analytic_tag_id
    #         })
    #     for tax_line in self.tax_line_ids:
    #         tax_line.update({
    #             'analytic_tag_ids': [(6, 0, self.analytic_tag_id.ids)],
    #             'account_analytic_id': self.account_analytic_id.id
    #         })

    @api.onchange('tax_line_ids')
    def onchange_tax_tags(self):
        for tax_line in self.tax_line_ids:
            tax_line.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_id.ids)],
                'account_analytic_id': self.account_analytic_id.id
            })

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    @api.onchange('analytic_account_id')
    def _onchange_invoice_line_account(self):
        self.update({
            'account_analytic_id': self.analytic_account_id.id
        })


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.onchange('account_id')
    def onchange_account_id(self):
        analytic_dimension_ids = self.account_id.analytic_dimension_ids
        dimensions = [val.analytic_dimension_id.id for val in analytic_dimension_ids]
        return {'domain': {
            'analytic_tag_ids': [('analytic_dimension_id', 'in', dimensions)],
           }}


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.model
    def create(self, vals):
        inv = vals['invoice_id']
        tax_val = self.env['account.invoice'].browse(inv)
        vals.update({
            'analytic_tag_ids': [(6, 0, tax_val.analytic_tag_id.ids)]
        })
        res = super(AccountInvoiceTax, self).create(vals)
        return res


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self).compute_refund()
        account = self.env['account.invoice'].browse(res['domain'][1][2][0])
        account.update({
            'analytic_tag_id': account.refund_invoice_id.analytic_tag_id.ids
        })
        for tax in account.tax_line_ids:
            tax.update({
                'analytic_tag_ids': account.refund_invoice_id.tax_line_ids.analytic_tag_ids.ids
            })
        return res
