from odoo import models, api, _
from odoo.exceptions import ValidationError


class InvoiceDomain(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.onchange('account_id')
    def onchange_account_id(self):
        analytic_dimension_ids = self.account_id.analytic_dimension_ids
        dimensions = [val.analytic_dimension_id.id for val in analytic_dimension_ids]
        return {'domain': {
            'analytic_tag_ids': [('analytic_dimension_id', 'in', dimensions)],
           }}


class SaleInvoice(models.Model):
    _inherit = 'account.invoice'

    # Invoice validate without sale/purchase reference

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
                    else:
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))

            allowed_tag_val = []
            for tag in tag_ids:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            invoice_ids.update({
                'analytic_tag_ids': [(6, 0, allowed_tag_val)]
            })
            if not invoice_ids.analytic_tag_ids:
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
                    else:
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
            allowed_tag_val = []
            for tag in tag_vals:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            self.update({
                'analytic_tag_id': [(6, 0, allowed_tag_val)]
            })
            if not self.analytic_tag_id:
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

        res = super(SaleInvoice, self).action_invoice_open()
        return res

    @api.model
    def create(self, vals):
        if vals.get('analytic_tag_ids'):
            vals.update({
                'analytic_tag_id': vals['analytic_tag_ids']
            })
        res = super(SaleInvoice, self).create(vals)
        return res


class AnalyticTagSale(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(AnalyticTagSale, self)._prepare_invoice()
        res.update({
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
        })
        return res


class TaxInvoice(models.Model):
    _inherit = 'account.invoice.tax'

    @api.model
    def create(self, vals):
        inv = vals['invoice_id']
        tax_val = self.env['account.invoice'].browse(inv)
        vals.update({
            'analytic_tag_ids': [(6, 0, tax_val.analytic_tag_id.ids)]
        })
        res = super(TaxInvoice, self).create(vals)
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

