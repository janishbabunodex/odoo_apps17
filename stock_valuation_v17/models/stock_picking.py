# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NxStockPicking(models.Model):
    _inherit = 'stock.picking'

    valuation_value = fields.Float(
        string="Total Value",
        compute="_compute_valuation_value",
        store=True,
    )

    @api.depends('move_ids.valuation_total')
    def _compute_valuation_value(self):
        for rec in self:
            rec.valuation_value = abs(
                sum(move.valuation_total for move in rec.move_ids)
            )


class NxStockMove(models.Model):
    _inherit = "stock.move"

    valuation_total = fields.Float(
        string="Total Value",
        compute="_compute_valuation_total",
        store=True,
    )

    @api.depends('stock_valuation_layer_ids.value')
    def _compute_valuation_total(self):
        for rec in self:
            rec.valuation_total = sum(
                valuation.value for valuation in rec.stock_valuation_layer_ids
            )
