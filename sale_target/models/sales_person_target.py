from odoo import api, fields, models


class SalesTarget(models.Model):
    _name = 'sale.target'

    name = fields.Char(string='Reference')
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    from_date = fields.Date(string="From Date")
    end_date = fields.Date(string="To Date")
    user_line = fields.One2many('sales.person', 'line_id', string="Salesperson List")

    @api.multi
    def get_sales(self):
        sales = []
        for line in self.user_line:
            if line:
                line.actual = 0
                line.pending = 0
        saleorder = self.env['account.invoice']
        for line in self.user_line:
            sales = saleorder.search([
                ('user_id', '=', line.user_id.id),
                ('date_invoice', '>=', self.from_date),
                ('date_invoice', '<=', self.end_date)
            ])
            if sales:
                for sale in sales:
                    for line in self.user_line:
                        if line.user_id == sale.user_id:
                            line.actual += sale.amount_total
                            line.pending = line.target - sale.amount_total
        return True


class SalesPerson(models.Model):
    _name = 'sales.person'

    user_id = fields.Many2one('res.users', string="Sales Person")
    target = fields.Float(string="Target")
    actual = fields.Float(string="Actual")
    pending = fields.Float(string="Pending")
    line_id = fields.Many2one('sale.target', string="Target Id")
