# -*- coding: utf-8 -*-
{
    'name': 'Inventory FSN Report',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Fast / Slow / Non-Moving inventory analysis with PDF & Excel export',
    'description': """
Inventory FSN Report
====================

Classify your inventory items as **Fast (F)**, **Slow (S)**, or **Non-Moving (N)**
based on the turnover ratio calculated over any user-defined date range.

Features
--------
* Date range selection for the analysis period
* Filter by Products, Product Categories
* Filter by Company and Warehouses
* FSN type filter — view All, Fast, Slow, or Non-Moving items
* Colour-coded list view with badge decoration
* Bar chart and Pivot views for quick visual analysis
* Export to **PDF** (QWeb report with legend)
* Export to **Excel** (.xlsx) with colour-coded FSN cells
* Turnover ratio formula: Sale Qty ÷ Average Stock

Classification Rules
--------------------
* **F — Fast Moving**: Turnover Ratio > 3
* **S — Slow Moving**: Turnover Ratio between 1 and 3
* **N — Non Moving**: Turnover Ratio ≤ 1
    """,
    'author': 'ASH',
    'website': 'https://www.ash.com',
    'support': 'support@ash.com',
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
    ],
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_fsn_data_report_views.xml',
        'wizard/inventory_fsn_report_wizard_views.xml',
        'report/inventory_fsn_report_templates.xml',
        'report/inventory_fsn_report_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 0,
    'currency': 'USD',
}
