# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_analytic_tags = fields.Many2many('account.analytic.tag',
                                         'tag_manufacture_rel',
                                         string='Analytic Tags')

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            picking_type_id = values.get(
                'picking_type_id') or self._get_default_picking_type()
            picking_type_id = self.env['stock.picking.type'].browse(
                picking_type_id)
            if picking_type_id:
                values['name'] = picking_type_id.sequence_id.next_by_id()
            else:
                values['name'] = self.env['ir.sequence'].next_by_code(
                    'mrp.production') or _('New')
        if not values.get('procurement_group_id'):
            values['procurement_group_id'] = self.env[
                "procurement.group"].create({'name': values['name']}).id
        production = super(MrpProduction, self).create(values)

        analytic_dimension_ids = []
        for tag in production.mrp_analytic_tags:
            analytic_dimension_ids.append(tag.analytic_dimension_id.id)
        if len(set(analytic_dimension_ids)) != len(analytic_dimension_ids):
            raise ValidationError(_
                                  (
                                      "You cannot set two tags from same dimension."))
        production._generate_moves()
        return production

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


class ManufacturingConsumedTags(models.Model):
    _inherit = 'stock.move'

    analytic_tag_ids = fields.Many2many('account.analytic.tag',
                                        string='Analytic Tags')
