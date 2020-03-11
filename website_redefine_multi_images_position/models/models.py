# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################


from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    multi_image_tab_position_settings = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('top', 'Top'),
        ('bottom','Bottom')], string="Set Multi-Images Position",default='bottom')

    # @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        value = self.multi_image_tab_position_settings or 'bottom'
        self.env['ir.config_parameter'].sudo().set_param('website_sale.multi_image_tab_position_settings', value)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            multi_image_tab_position_settings=params.get_param('website_sale.multi_image_tab_position_settings', default='bottom'))
        return res

    
    @api.model
    def enable_multi_images_settings(self):
        res_config_setting_obj = self.create({
            'group_website_multiimage':True,
            'multi_image_tab_position_settings':'left'
        })
        res_config_setting_obj.execute()