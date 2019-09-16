# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    analytic_tag_ids = fields.Many2many('account.analytic.tag',
                                        string='Analytic Tags')

    @api.multi
    def button_validate(self):
        super(StockLandedCost, self).button_validate()
        dimension_tags_allowed = []
        for line in self.account_move_id.line_ids:
            tag_ids = self.analytic_tag_ids.ids
            for dimension in line.account_id.analytic_dimension_ids:
                dimension_tags = dimension.analytic_dimension_id.analytic_tag_ids.ids
                dimension_tags_allowed += dimension_tags
                occurance = False
                for x in set(dimension_tags):
                    if tag_ids.count(x) > 0:
                        occurance = True
                if occurance is False:
                    if dimension.default_value:
                        tag_ids.append(dimension.default_value.id)
                    else:
                        raise ValidationError(_("Please choose a valid Tag for dimension: %s  and account: %s") % (
                            dimension.analytic_dimension_id.name, line.account_id.code))
            allowed_tag_val = []
            for tag in tag_ids:
                if tag in dimension_tags_allowed:
                    allowed_tag_val.append(tag)
            line.update({
                'analytic_tag_ids': [(6, 0, allowed_tag_val)]
            })
            if not line.analytic_tag_ids:
                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
        return True
