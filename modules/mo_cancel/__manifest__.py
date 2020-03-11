# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Manufacturing Order',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Manufacturing',
    'maintainer': 'Craftsync Technologies',
   
    'summary': """Cancel manufacturings Order app is helpful plugin to cancel processed manufacturing order. Cancellation of manufacturing order includes operations like cancel Invoice, Cancel Delivery Order, Cancel paid Invoice, Unreconcile Payment, Cancel processed delivery order/ cancel processed picking.""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['mrp'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_manufacturing_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 19.00,
    'currency': 'EUR',

}
