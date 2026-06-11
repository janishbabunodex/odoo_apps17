{
    'name': 'Vendor Product Code',
    'version': '17.0.1.0.0',
    'summary': 'Assign vendor-specific prefixes to auto-generate unique product barcodes',
    'description': """
Vendor Product Code
===================

This module allows you to assign a **Product Prefix** to each supplier (vendor)
and automatically generate unique product barcodes based on that prefix.

Key Features
------------
* Add a **Product Prefix** (4 alphanumeric characters) to any supplier.
* Auto-generate a unique barcode for a product with one click using the
  supplier's prefix + an auto-incrementing sequence.
* Once a barcode is generated, the barcode field becomes read-only to prevent
  accidental changes.
* Validates that only valid 4-character alphanumeric prefixes are accepted.
* Works seamlessly with Odoo's standard Purchase workflow.

Use Case
--------
Useful for businesses that source products from multiple vendors and want
barcodes that encode the vendor identity directly.
    """,
    'author': 'ASH',
    'company': 'ASH',
    'maintainer': 'ASH',
    'website': 'www.ash.com',
    'category': 'Inventory/Purchase',
    'license': 'LGPL-3',
    'depends': ['base', 'purchase'],
    'data': [
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
