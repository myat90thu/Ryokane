{
    "name": "Sales target for salesperson",
    "version": "12.0.1.0.0",
    "author": "BAS",
    "summary": "Sales target for salesperson",
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    "depends": [
        "sale_management","crm","account"
    ],
    'data': [
    'views/saletarget_views.xml',
    'security/ir.model.access.csv',

    ],
    'demo': [
       
    ],
    'installable': True,
}