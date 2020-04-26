# -*- coding: utf-8 -*-
from odoo import api, models, fields


class res_partner(models.Model):
    _inherit = "res.partner"

    add_product_from_history = fields.Boolean('In Future Auto Add Product From SO')
    visible_product_ids = fields.Many2many('product.template', 'partner_product_rel', 'partner_id', 'product_id', string='Visible Products')
    visible_audience_ids = fields.Many2many('product.website.audience', 'partner_audi_rel', 'partner_id', 'audi_id', string="Visible Product Audience")

    @api.multi
    def add_all_product(self):
        visible_product_ids = [prod.id for prod in self.env['product.template'].search([])]
        if visible_product_ids:
            self.visible_product_ids = visible_product_ids

    @api.multi
    def add_all_category(self):
        visible_audience_ids = [audi.id for audi in self.env['product.website.audience'].search([])]
        if visible_audience_ids:
            self.visible_audience_ids = visible_audience_ids
        return True


class WebsiteAudience(models.Model):
    _name = "product.website.audience"

    name = fields.Char()


class Product(models.Model):
    _inherit = "product.template"

    audience_id = fields.Many2one('product.website.audience', string="Website Audience")
