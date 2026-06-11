# -*- coding: utf-8 -*-
from odoo import fields, models


class InventoryFsnDataReport(models.TransientModel):
    """
    Stores one row of FSN report data per product/location combination.
    Linked back to the wizard record via data_id so the tree/graph/pivot views
    can domain-filter to the current report run.
    """
    _name = 'inventory.fsn.data.report'
    _description = 'Inventory FSN Data Report'

    data_id = fields.Many2one(
        comodel_name='inventory.fsn.report.wizard',
        string='Report',
        ondelete='cascade',
    )

    # ── Product info ─────────────────────────────────────────────────────────
    product_id = fields.Many2one('product.product', string='Product')
    internal_ref = fields.Char(string='Internal Reference')
    product_name = fields.Char(string='Product Name')
    category_id = fields.Many2one('product.category', string='Category')
    category_name = fields.Char(string='Category Name')

    # ── Location ─────────────────────────────────────────────────────────────
    location_id = fields.Many2one('stock.location', string='Location')
    location_name = fields.Char(string='Location Name')

    # ── Stock figures ────────────────────────────────────────────────────────
    opening_stock = fields.Float(string='Opening Stock', digits=(16, 2))
    closing_stock = fields.Float(string='Closing Stock', digits=(16, 2))
    average_stock = fields.Float(string='Average Stock', digits=(16, 2))
    sale_qty = fields.Float(string='Sale Qty', digits=(16, 2))
    turnover_ratio = fields.Float(string='Turnover Ratio', digits=(16, 4))

    # ── FSN classification ───────────────────────────────────────────────────
    mark = fields.Selection(
        selection=[
            ('F', 'Fast Moving'),
            ('S', 'Slow Moving'),
            ('N', 'Non Moving'),
        ],
        string='FSN',
    )
