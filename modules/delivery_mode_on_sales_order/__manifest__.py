{
    "name": "Sales order delivery mode",
    "version": "12.0.1.0.0",
    "author": "BAS",
    "summary": "Display delivery mode in sales order",
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    "depends": [
        "account",
        "sale_management",
    ],
    'data': [
    'views/saleorder_views.xml',
    'security/ir.model.access.csv',
    'demo/data.xml'
    ],
    'demo': [
       
    ],
    'installable': True,
}