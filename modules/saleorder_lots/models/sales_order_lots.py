from odoo import _, api, fields, models
from datetime import datetime
import dateutil.parser
    
class AccountSalesOrderLine(models.Model):
    _inherit = "sale.order.line"
   
    prod_lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        compute='_compute_prod_lots',
        string="Production Lots",
    )

    lot_formatted_note = fields.Html(
        string='Formatted Note',
        compute='_compute_line_lots',
    )
    
    @api.multi
    def _compute_prod_lots(self):
        for line in self:
            line.prod_lot_ids = line.mapped(
                'move_ids.active_move_line_ids.lot_id'
            )

    @api.multi
    def _compute_line_lots(self):
        for line in self:
            note = '<ul>'
            lot_strings = []
            for sml in line.mapped('move_ids.move_line_ids'):
                if sml.lot_id:

                    if sml.product_id.tracking == 'serial':
                        lot_strings.append('<li>%s %s</li>' % (
                            _('S/N'), sml.lot_id.name, 
                        ))
                    else:
                        
                            lot_strings.append('<li style="word-spacing:5px">%s %s Q :(%s) DDM :%s</li>' % (
                        _   ('Lot'), sml.lot_id.name, sml.product_uom_qty,sml.lot_id.use_date
                            ))
                    
            if lot_strings:
                note += ' '.join(lot_strings)
                note += '</ul>'
                line.lot_formatted_note = note