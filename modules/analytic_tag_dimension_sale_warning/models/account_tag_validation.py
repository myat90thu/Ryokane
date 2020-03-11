from odoo import models, api, _
from odoo.exceptions import ValidationError


class AnalyticTagSale(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(AnalyticTagSale, self)._prepare_invoice()
        res.update({
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
        })
        return res


class JournalInvoice(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        res = super(JournalInvoice, self).create(vals)
        invoice_id = res.invoice_id
        if invoice_id:
            analytic_tag_id = invoice_id.analytic_tag_id
            if res.user_type_id.type == "payable":
                res.analytic_tag_ids = analytic_tag_id.ids
            if res.user_type_id.type == "receivable":
                res.analytic_tag_ids = analytic_tag_id.ids
        return res

