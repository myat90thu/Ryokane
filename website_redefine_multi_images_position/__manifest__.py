# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Redefine Multi Images Position",
  "summary"              :  "The website user can now select the position of the product carousel on the product page. The multi images can be placed at left, right, top or bottom of the product image.",
  "category"             :  "Website",
  "version"              :  "1.1.45",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Redefine-Multi-Images-Position.html",
  "description"          :  """Odoo Website Redefine Multi Images Position
Multiple product images
Product image carousels
Product images layouts
Stack product images on website
Product image position
Product Multiple images position
Product image position left
Product image position right
Product image position top
Product image position bottom
Website Shift Multi Images Position
Different Multi Images Position
Website Shift Images
Images Tab in Left""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_redefine_multi_images_position",
  "depends"              :  ['base','web','website_sale'],
  "data"                 :  [
                             'views/templates.xml',
                             'views/product.xml',
                             'views/res_config_settings_views.xml',
                            ],
  "demo"                 :  ['demo/demo_data.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}