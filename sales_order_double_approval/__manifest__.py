{
    'name': 'Sales Order double approval workflow',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
       """
    """,
    'summary': 'Odoo module that Allow you to Double Approve process Workflow into sales orders',
    'author': 'BAS',
    'website': '',
    'depends': [ 'sale_management','sale', 'digest'],
    'data': [
        'security/security.xml',
        'view/res_config_settings_views.xml',
        'view/account_salesorder_views.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}