from odoo import _, api, fields, models


class deliverymode(models.Model):
    _name='delivery.mode'
    _description = "Delivery mode"
    _order = 'sequence, id'

    name=fields.Char(string='Delivery mode', required=True, translate=True)
    code=fields.Char(string='Delivery code', required=True, translate=True)
    sequence = fields.Integer(default=1)
    saleorder_id = fields.One2many('sale.order', 'delivery_mode', string="Delivery Mode")
class deliverymodeforsale(models.Model):
    _inherit = 'sale.order'

    delivery_mode = fields.Many2one('delivery.mode',string="Mode de livraison")
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'delivery_mode':self.delivery_mode.id,
            'analytic_tag_ids':[(6,0,self.analytic_tag_ids.ids)],
            'incoterm_id':self.incoterm.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
        }
        return invoice_vals

class deliverymodeforinvoice(models.Model):
    _inherit = 'account.invoice'
    _name='account.invoice'
    delivery_mode=fields.Many2one('delivery.mode',string='Delivery mode')
