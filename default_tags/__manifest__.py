# -*- coding: utf-8 -*-
{
    'name': "Default Tags",
    'summary': """
       """,
    'author': 'Wafi Chaar',
    'company': 'HLOUL-BAS',
    'category': 'Sale',
    'website': 'https://www.hloul-bas.com',
    'version': '12.0.1.0.1',
    'depends': ['base', 'purchase', 'sale', 'contacts', 'stock_landed_costs'],
    'data': [
        'views/order_line.xml',
        'views/manufacturing_view.xml',
        'views/payment_view.xml',
        'views/stock_landed_cost_view.xml',
        # 'views/account_invoice_view.xml'
    ],
    'installable': True,
}
