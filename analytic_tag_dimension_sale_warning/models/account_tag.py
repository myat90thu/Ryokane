from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DimensionLine(models.Model):
    _inherit = 'account.analytic.dimension'

    color_index = fields.Integer(String='Colour Index')

    # Validation for unique Analytic tags in dimension

    @api.constrains('analytic_tag_ids')
    def onchange_analytic_tag_ids(self):
        for tag in self.analytic_tag_ids:
            if tag.active_tag == True:
                raise ValidationError(_("Tags already exist!!!"))


class DimensionLineOrder(models.Model):
    _inherit = 'account.analytic.tag'

    color = fields.Integer(String='Colour Index')
    active_tag = fields.Boolean(String='Active')

    # Validation for unique Analytic tags in stock picking line


class StockPickingValidate(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        for picking in self.move_ids_without_package:
            dimension_ids = []
            for tags in picking.analytic_tag_ids:
                dimension_ids.append(tags.analytic_dimension_id.id)
            if len(set(dimension_ids)) != len(dimension_ids):
                raise ValidationError(_
                            ("You cannot set two tags from same dimension."))
        res = super(StockPickingValidate, self).button_validate()
        return res


