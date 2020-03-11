# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class OrderLine(models.Model):
    _inherit = 'account.payment'

    analytic_tag_ids = fields.Many2many('account.analytic.tag',
                                        string='Journal Analytic Tags')
    partner_analytic_tags = fields.Many2many('account.analytic.tag',
                            'rel_account_tag', string='Partner Analytic Tags')

# Inherit analytic tags on orderlines on onchange orderline(sale order)


class OrderLineSale(models.Model):
    _inherit = 'sale.order'

    @api.onchange('order_line')
    def _onchange_sale_order_line(self):
        if self.analytic_tag_ids:
            self.order_line.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })

# Inherit analytic tags on orderlines on onchange orderline(purchase order)


class OrderLinePurchase(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('order_line')
    def _onchange_purchase_order_line(self):
        if self.analytic_tag_ids:
            self.order_line.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })
        if self.analytic_account_id:
            self.order_line.update({
                'account_analytic_id': self.analytic_account_id.id
            })




