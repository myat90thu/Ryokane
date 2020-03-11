{
    "name": "Sales order production Lots",
    "version": "12.0.1.0.0",
    "author": "BAS",
    "summary": "Display delivered serial numbers in sales order",
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    "depends": [
        "account",
        "sale_management",
        "stock_picking_invoice_link",
    ],
    'data': [
    'views/account_saleorder_views.xml',
    'reports/report_saleorder.xml',
    ],
    'demo': [
        'demo/sale.xml',
    ],
    'installable': True,
}