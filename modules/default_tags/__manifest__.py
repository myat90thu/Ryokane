# -*- coding: utf-8 -*-
{
    'name': "Default Tags",
    'summary': """
       """,
    'author': 'Wafi Chaar',
    'company': 'BAS',
    'category': 'Sale',
    'website': 'https://www.bas.sarl',
    'version': '12.0.1.0.3',
    'depends': ['base', 'purchase', 'sale', 'contacts', 'stock_landed_costs'],
    'data': [
        'views/order_line.xml',
        'views/manufacturing_view.xml',
        'views/payment_view.xml',
        'views/stock_landed_cost_view.xml',
    ],
    'installable': True,
}
