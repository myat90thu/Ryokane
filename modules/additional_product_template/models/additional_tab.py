from odoo import models, fields, api, _

tab = [('horizontal','Horizontal'), ('vertical','Vertical'),]

class additionalproducttab(models.Model):
    _name= 'additional.product.tab'

    enabled=fields.Boolean(default=1)
    name=fields.Char(required=1,translate=True)
    seq=fields.Integer()
    contents= fields.Html(require=1, translate= True)
    tab_pr_id= fields.Many2one('product.template',string = 'Product')

class Product(models.Model):
    _inherit='product.template'
    
    pr_tab_type = fields.Selection(selection = tab, string= 'Tab Layout', default='vertical')

    additional_pr_tab_ids = fields.One2many('additional.product.tab','tab_pr_id',string= 'Product Tabs', domain=['|',('enabled','=',True),('enabled','=',False)])