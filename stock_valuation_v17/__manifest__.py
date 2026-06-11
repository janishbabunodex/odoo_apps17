# -*- coding: utf-8 -*-
{
    'name': 'Stock Valuation',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Display total valuation value on stock pickings and moves',
    'description': """
Stock Valuation
===============
Adds computed valuation totals on stock picking and stock move records.

Features:
---------
* Displays total stock valuation value on each stock picking list & form
* Computes valuation per stock move from valuation layers
* Fully integrated with Odoo's stock_account module
    """,
    'author': 'ASH',
    'website': 'https://www.ash.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'stock_account',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
