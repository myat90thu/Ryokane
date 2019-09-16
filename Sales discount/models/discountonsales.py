from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
class discountonsale(models.Model):
    _inherit = "sale.order"

    untaxed_focamount= fields.Float(compute='_amount_all',string="Amount")
    foc_percentage = fields.Float(string='FOC Value', digits=dp.get_precision('FOC Value'),compute='_amount_all')

    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        foc_total=0
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed =untaxed_focamount= amount_tax = 0.0
            for line in order.order_line:
                if line.discount == 100:
                    foc_total+=line.price_unit * line.product_uom_qty
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if amount_untaxed == 0:
                untaxed_focamount=0
            else:
                untaxed_focamount+=foc_total/amount_untaxed  
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
                'untaxed_focamount':foc_total,
                'foc_percentage':untaxed_focamount * 100 ,
            })
