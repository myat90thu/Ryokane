from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update(reservation=ui_order.get("reservation"), practitioner=ui_order.get("practitioner"))
        return res

    practitioner = fields.Many2one(comodel_name="hr.employee", string="Practitioner")
    reservation = fields.Many2one('reservation', string="Reservation")


class Reservation(models.Model):
    _name = 'reservation'

    name = fields.Char(string="Reservation")
    reservation_analytic_tags = fields.Many2one('account.analytic.tag', string='Analytic Tags')
