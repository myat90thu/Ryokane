{
    'name': 'Sale Free of Charge (FOC)',
    'version': '12.0.1.0.0',
    'category': 'Sales Discount',
    'summary': 'Adds FOC products to sale order ',
    'author': 'BAS',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'sale_management','sale', 'digest'
    ],
    'data': [
        'views/salediscount.xml',
        
    ],
    'installable': True,
}