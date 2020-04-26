# -*- coding: utf-8 -*-
from odoo import api, models, fields
from mock.mock import self


class public_product(models.Model):
    _name = 'public.product'

    test = fields.Boolean("TEST")
    public_visible_product_ids = fields.Many2many('product.template', 'public_product_rel', 'public_id', 'product_id', string='Products')
    public_visible_audience_ids = fields.Many2many('product.website.audience', 'public_audi_rel', 'public_id', 'audi_id', string="Product Audience")

    @api.model
    def default_get(self, fields):
        result = super(public_product, self).default_get(fields)
        public_product_id = self.search([], limit=1, order="id desc")
        if public_product_id:
            public_visible_product_ids = [visible_prod.id for visible_prod in public_product_id.public_visible_product_ids]
            public_visible_audience_ids = [visible_audi.id for visible_audi in public_product_id.public_visible_audience_ids]
            result.update({'public_visible_product_ids': [(6, 0, public_visible_product_ids)]})
            result.update({'public_visible_audience_ids': [(6, 0, public_visible_audience_ids)]})
        return result

    @api.multi
    def add_all_product(self):
        public_visible_product_ids = [prod.id for prod in self.env['product.template'].search([])]
        if public_visible_product_ids:
            self.public_visible_product_ids = public_visible_product_ids
        return True

    @api.multi
    def add_all_category(self):
        public_visible_audience_ids = [audi.id for audi in self.env['product.website.audience'].search([])]
        if public_visible_audience_ids:
            self.public_visible_audience_ids = public_visible_audience_ids
        return True

    @api.multi
    def write(self, vals):
        res = super(public_product, self).write(vals)
        partner = self.env.ref('base.public_partner')
        partner_vals = {
            'visible_product_ids': self.public_visible_product_ids,
            'visible_audience_ids': self.public_visible_audience_ids
        }
        partner.update(partner_vals)
        return res
