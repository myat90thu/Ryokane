from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update(reservation=ui_order.get("reservation"), pratitioner=ui_order.get("pratitioner"))
        return res

    pratitioner = fields.Many2one(comodel_name="hr.employee", string="Pratitioner")
    reservation = fields.Selection(
        selection=[("walk_in", "Walk In"), ("phone", "Phone"), ("internet", "Internet")], string="Reservation"
    )
