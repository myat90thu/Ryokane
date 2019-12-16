
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class Pricelistitem(models.Model):
    _inherit = "product.pricelist.item"
    
    pricelist_formatted_table = fields.Html(
        string='Formatted table',
        compute='_compute_price_for_all_pricelists',
    )


    def _compute_price_for_all_pricelists(self):
        pricelists = []
        productperpricelist=[]
        priceperproduct=[]
        pricelist_formatted_table.append('<table style="width:100%">')
        for record in self:
            pricelists.append(record.pricelist_id)
            productperpricelist.append(record.product_id)
            priceperproduct.append(record.fixed_price)
        for pricelist in pricelists:
            pricelist_formatted_table.append('<tr> <th>'+ pricelist +'</th></tr>')
        for product in productperpricelist:
            pricelist_formatted_table.append('<tr> <td>'+ product +'</td></tr>')
        for price in priceperproduct:
            pricelist_formatted_table.append('<tr> <td>'+ price +'</td></tr></table>')
