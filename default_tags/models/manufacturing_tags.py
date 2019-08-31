# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_analytic_tags = fields.Many2many('account.analytic.tag',
                                         'tag_manufacture_rel',
                                         string='Analytic Tags')

    @api.onchange('mrp_analytic_tags')
    def onchange_mrp_tags(self):
        analytic_dimension_ids = []
        for tag in self.mrp_analytic_tags:
            analytic_dimension_ids.append(tag.analytic_dimension_id.id)
        if len(set(analytic_dimension_ids)) != len(analytic_dimension_ids):
            raise ValidationError(_
                (
                "You cannot set two tags from same dimension."))
        for mrp_tags in self.move_raw_ids:
            mrp_tags.update({
                'analytic_tag_ids': self.mrp_analytic_tags.ids
            })


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        res = super(MrpProductProduce, self).do_produce()
        for move in self.production_id.move_finished_ids:
            move.update({
                'analytic_tag_ids': [(6, 0, self.production_id.mrp_analytic_tags.ids)]
            })
        for move in self.production_id.move_raw_ids:
            move.update({
                'analytic_tag_ids': [(6, 0, self.production_id.mrp_analytic_tags.ids)]
            })
        stock_move_lines = self.env['stock.move.line'].search([('production_id', '=', self.production_id.id)])
        for stock_move_line in stock_move_lines:
            if stock_move_line.product_qty != stock_move_line.qty_done:
                stock_move_line.update({
                    'product_uom_qty': stock_move_line.qty_done
                })
        return res
