from odoo import api, fields, models,exceptions
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from odoo.addons.mrp.models.stock_move import StockMove


class Stock_Move(models.Model):
    _inherit = 'stock.move'

    def _action_cancel(self):
        # if any(move.quantity_done and (move.raw_material_production_id or move.production_id) for move in self):
        #     raise exceptions.UserError(_('You cannot cancel a manufacturing order if you have already consumed material.\
        #      If you want to cancel this MO, please change the consumed quantities to 0.'))
        return super(StockMove, self)._action_cancel()

    StockMove._action_cancel = _action_cancel

class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def action_cancel(self):
        quant_obj = self.env['stock.quant']
        account_move_obj = self.env['account.move']
        stk_mv_obj = self.env['stock.move']
        for order in self:
            
            if order.company_id.cancel_inventory_move_for_mo:
                moves = stk_mv_obj.search(['|',('production_id', '=', order.id),('raw_material_production_id','=',order.id)])
                for move in moves:
                    if move.state == 'cancel':
                        continue
                    # move._do_unreserve()
                    if move.state == "done" and move.product_id.type == "product":
                        for move_line in move.move_line_ids:
                            quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1)
                    if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                        move.state = 'waiting'
                    elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                        move.state = 'waiting'
                    else:
                        move.state = 'confirmed'
                    siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                    if move.propagate:
                        # only cancel the next move if all my siblings are also cancelled
                        if all(state == 'cancel' for state in siblings_states):
                            move.move_dest_ids._action_cancel()
                    else:
                        if all(state in ('done', 'cancel') for state in siblings_states):
                            move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                    account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                    if account_moves:
                        for account_move in account_moves:
                            account_move.quantity_done = 0.0
                            account_move.button_cancel()
                            account_move.unlink()

            if order.company_id.cancel_work_order_for_mo:
                order.workorder_ids.action_cancel()
                    
        res = super(ManufacturingOrder, self).action_cancel()
        return True

# class MrpWorkorder(models.Model):
#     _inherit = 'mrp.workorder'

#     @api.multi
#     def write(self, values):
#         if list(values.keys()) != ['time_ids'] and any(workorder.state == 'done' for workorder in self):
#             raise UserError(_('You can not change the finished work order.'))
#         return super(MrpWorkorder, self).write(values)
