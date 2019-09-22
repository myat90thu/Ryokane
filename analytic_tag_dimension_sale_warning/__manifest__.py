{
    "name": "Analytic Tag Dimension Sale Warning",
    "summary": "Group Analytic Entries by Dimensions",
    "category": "Accounting",
    "version": "12.0.1.0.2",
    "author": "Wafi Chaar",
    "website": "https://www.hloul-bas.com",
    "depends": ['base', 'analytic_tag_dimension',
                'sale', 'purchase', 'stock', 'account'
    ],
    "data": [
             'views/analytic_tag_view.xml',
             'views/dimension_group.xml',
             'views/analytic_tax_view.xml',
             'security/ir.model.access.csv'
             ],
    "auto_install": True,
}