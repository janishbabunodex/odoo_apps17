# -*- coding: utf-8 -*-
import base64
import io

import xlsxwriter

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class InventoryFsnReportWizard(models.TransientModel):
    _name = 'inventory.fsn.report.wizard'
    _description = 'Inventory FSN Report Wizard'

    # ── Date Range ───────────────────────────────────────────────────────────
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    # ── FSN Filter ───────────────────────────────────────────────────────────
    fsn_filter = fields.Selection(
        selection=[
            ('all', 'All'),
            ('F', 'Fast Moving (F)'),
            ('S', 'Slow Moving (S)'),
            ('N', 'Non Moving (N)'),
        ],
        string='FSN Type',
        default='all',
        required=True,
    )

    # ── Filters ──────────────────────────────────────────────────────────────
    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Products',
    )
    category_ids = fields.Many2many(
        comodel_name='product.category',
        string='Categories',
    )

    # ── Domains ──────────────────────────────────────────────────────────────
    company_ids = fields.Many2many(
        comodel_name='res.company',
        string='Companies',
        default=lambda self: self.env.company,
    )
    warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        string='Warehouses',
    )

    # ────────────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────────────

    def _get_customer_location_id(self):
        """Return the ID of the virtual customer location (usage='customer')."""
        location = self.env['stock.location'].search(
            [('usage', '=', 'customer')], limit=1
        )
        if not location:
            raise UserError(_('No customer location found in the system.'))
        return location.id

    def _get_warehouse_location_ids(self):
        """
        Return internal location IDs to filter stock moves by.
        Uses selected warehouses' lot_stock_id children if provided;
        otherwise all internal locations for the selected companies.
        """
        if self.warehouse_ids:
            parent_locations = self.warehouse_ids.mapped('lot_stock_id')
        else:
            parent_locations = self.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('company_id', 'in', self.company_ids.ids or [self.env.company.id]),
            ])
        all_locations = self.env['stock.location'].search([
            ('id', 'child_of', parent_locations.ids),
        ])
        return all_locations.ids

    # ────────────────────────────────────────────────────────────────────────
    # Core SQL query
    # ────────────────────────────────────────────────────────────────────────

    def _get_report_data(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(_('Start Date must be before End Date.'))

        customer_loc_id = self._get_customer_location_id()
        location_ids = self._get_warehouse_location_ids()

        if not location_ids:
            raise UserError(_(
                'No internal locations found for the selected warehouses/companies.'
            ))

        params = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'customer_loc': customer_loc_id,
            'location_ids': tuple(location_ids),
        }

        product_filter = ''
        category_filter = ''

        if self.product_ids:
            params['product_ids'] = tuple(self.product_ids.ids)
            product_filter = 'AND sm.product_id IN %(product_ids)s'

        if self.category_ids:
            params['category_ids'] = tuple(self.category_ids.ids)
            category_filter = 'AND pt.categ_id IN %(category_ids)s'

        query = f"""
            WITH movements AS (
                -- Incoming moves  (destination is an internal location we track)
                SELECT
                    sm.product_id,
                    sm.location_dest_id                                              AS location_id,
                    SUM(sm.product_uom_qty) FILTER (WHERE sm.date <  %(date_start)s) AS in_open,
                    SUM(sm.product_uom_qty) FILTER (WHERE sm.date <= %(date_end)s)   AS in_close,
                    SUM(sm.product_uom_qty) FILTER (
                        WHERE sm.date BETWEEN %(date_start)s AND %(date_end)s
                          AND sm.location_id = %(customer_loc)s
                    )                                                                AS sales_in,
                    0::numeric AS out_open,
                    0::numeric AS out_close,
                    0::numeric AS sales_out
                FROM stock_move sm
                JOIN product_product pp ON pp.id = sm.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE sm.state = 'done'
                  AND sm.location_dest_id IN %(location_ids)s
                  {product_filter}
                  {category_filter}
                GROUP BY sm.product_id, sm.location_dest_id

                UNION ALL

                -- Outgoing moves  (source is an internal location we track)
                SELECT
                    sm.product_id,
                    sm.location_id,
                    0::numeric AS in_open,
                    0::numeric AS in_close,
                    0::numeric AS sales_in,
                    SUM(sm.product_uom_qty) FILTER (WHERE sm.date <  %(date_start)s) AS out_open,
                    SUM(sm.product_uom_qty) FILTER (WHERE sm.date <= %(date_end)s)   AS out_close,
                    SUM(sm.product_uom_qty) FILTER (
                        WHERE sm.date BETWEEN %(date_start)s AND %(date_end)s
                          AND sm.location_dest_id = %(customer_loc)s
                    )                                                                AS sales_out
                FROM stock_move sm
                JOIN product_product pp ON pp.id = sm.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE sm.state = 'done'
                  AND sm.location_id IN %(location_ids)s
                  {product_filter}
                  {category_filter}
                GROUP BY sm.product_id, sm.location_id
            ),
            final AS (
                SELECT
                    m.product_id,
                    m.location_id,
                    COALESCE(SUM(m.in_open),  0) - COALESCE(SUM(m.out_open),  0) AS opening_stock,
                    COALESCE(SUM(m.in_close), 0) - COALESCE(SUM(m.out_close), 0) AS closing_stock,
                    (
                        COALESCE(SUM(m.in_open),  0) - COALESCE(SUM(m.out_open),  0) +
                        COALESCE(SUM(m.in_close), 0) - COALESCE(SUM(m.out_close), 0)
                    ) / 2.0                                                        AS average_stock,
                    COALESCE(SUM(m.sales_out), 0) - COALESCE(SUM(m.sales_in), 0)  AS sale_qty
                FROM movements m
                GROUP BY m.product_id, m.location_id
            )
            SELECT
                f.product_id,
                f.location_id,
                pp.default_code                       AS internal_ref,
                pt.name->>'en_US'                     AS product_name,
                pt.categ_id,
                pc.name                               AS category_name,
                sl.complete_name                      AS location_name,
                f.opening_stock,
                f.closing_stock,
                f.average_stock,
                f.sale_qty,
                CASE
                    WHEN f.average_stock <> 0 THEN f.sale_qty / f.average_stock
                    ELSE 0
                END                                   AS turnover_ratio,
                CASE
                    WHEN (CASE WHEN f.average_stock <> 0 THEN f.sale_qty / f.average_stock ELSE 0 END) > 3
                        THEN 'F'
                    WHEN (CASE WHEN f.average_stock <> 0 THEN f.sale_qty / f.average_stock ELSE 0 END) > 1
                        THEN 'S'
                    ELSE 'N'
                END                                   AS mark
            FROM final f
            JOIN product_product  pp ON pp.id = f.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN product_category pc ON pc.id = pt.categ_id
            JOIN stock_location   sl ON sl.id = f.location_id
        """

        if self.fsn_filter != 'all':
            query = f"SELECT * FROM ({query}) sub WHERE sub.mark = %(fsn_filter)s"
            params['fsn_filter'] = self.fsn_filter

        query += ' ORDER BY product_name, location_name'

        self.env.cr.execute(query, params)
        return self.env.cr.dictfetchall()

    # ────────────────────────────────────────────────────────────────────────
    # Actions
    # ────────────────────────────────────────────────────────────────────────

    def _save_report_rows(self, data):
        """Delete stale rows for this wizard run and create fresh ones."""
        self.env['inventory.fsn.data.report'].search(
            [('data_id', '=', self.id)]
        ).unlink()

        vals_list = []
        for row in data:
            vals_list.append({
                'data_id':        self.id,
                'product_id':     row.get('product_id'),
                'internal_ref':   row.get('internal_ref') or '',
                'product_name':   row.get('product_name') or '',
                'category_id':    row.get('categ_id'),
                'category_name':  row.get('category_name') or '',
                'location_id':    row.get('location_id'),
                'location_name':  row.get('location_name') or '',
                'opening_stock':  row.get('opening_stock') or 0.0,
                'closing_stock':  row.get('closing_stock') or 0.0,
                'average_stock':  row.get('average_stock') or 0.0,
                'sale_qty':       row.get('sale_qty') or 0.0,
                'turnover_ratio': row.get('turnover_ratio') or 0.0,
                'mark':           row.get('mark') or 'N',
            })
        if vals_list:
            self.env['inventory.fsn.data.report'].create(vals_list)

    def action_view_report(self):
        """Generate report rows and open them in tree + graph views."""
        self.ensure_one()
        data = self._get_report_data()
        self._save_report_rows(data)

        graph_view_id = self.env.ref(
            'nx_inventory_fsn_report.inventory_fsn_data_report_view_graph'
        ).id
        tree_view_id = self.env.ref(
            'nx_inventory_fsn_report.inventory_fsn_data_report_view_tree'
        ).id

        graph_first = self.env.context.get('graph_report', False)
        if graph_first:
            views = [(graph_view_id, 'graph'), (tree_view_id, 'tree')]
            view_mode = 'graph,tree'
        else:
            views = [(tree_view_id, 'tree'), (graph_view_id, 'graph')]
            view_mode = 'tree,graph'

        return {
            'name': _('Inventory FSN Report'),
            'domain': [('data_id', '=', self.id)],
            'res_model': 'inventory.fsn.data.report',
            'view_mode': view_mode,
            'type': 'ir.actions.act_window',
            'views': views,
        }

    def action_print_pdf(self):
        self.ensure_one()
        data = self._get_report_data()
        return self.env.ref(
            'nx_inventory_fsn_report.action_report_inventory_fsn'
        ).report_action(self, data={
            'report_data': data,
            'wizard': {
                'date_start': str(self.date_start),
                'date_end': str(self.date_end),
                'fsn_filter': dict(
                    self._fields['fsn_filter'].selection
                ).get(self.fsn_filter, 'All'),
            },
        })

    def action_export_excel(self):
        self.ensure_one()
        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('FSN Report')

        # ── Formats ──────────────────────────────────────────────────────────
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#4B3869', 'font_color': '#FFFFFF',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
        })
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
        })
        sub_fmt = workbook.add_format({
            'italic': True, 'align': 'center', 'font_color': '#555555',
        })
        cell_fmt = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        num_fmt = workbook.add_format({
            'border': 1, 'num_format': '#,##0.00', 'valign': 'vcenter',
        })
        f_fmt = workbook.add_format({
            'border': 1, 'bold': True,
            'font_color': '#006100', 'bg_color': '#C6EFCE', 'align': 'center',
        })
        s_fmt = workbook.add_format({
            'border': 1, 'bold': True,
            'font_color': '#9C6500', 'bg_color': '#FFEB9C', 'align': 'center',
        })
        n_fmt = workbook.add_format({
            'border': 1, 'bold': True,
            'font_color': '#9C0006', 'bg_color': '#FFC7CE', 'align': 'center',
        })
        mark_fmts = {'F': f_fmt, 'S': s_fmt, 'N': n_fmt}

        # ── Title rows ────────────────────────────────────────────────────────
        sheet.merge_range(0, 0, 0, 9, 'Inventory FSN Report', title_fmt)
        sheet.set_row(0, 24)
        fsn_label = dict(self._fields['fsn_filter'].selection).get(self.fsn_filter, 'All')
        sheet.merge_range(
            1, 0, 1, 9,
            f"Period: {self.date_start}  to  {self.date_end}   |   FSN Filter: {fsn_label}",
            sub_fmt,
        )

        # ── Column headers ────────────────────────────────────────────────────
        headers = [
            'Internal Ref', 'Product', 'Category', 'Location',
            'Opening Stock', 'Closing Stock', 'Avg Stock',
            'Sale Qty', 'Turnover Ratio', 'FSN',
        ]
        col_widths = [14, 32, 22, 26, 14, 14, 12, 12, 14, 6]
        for col, (h, w) in enumerate(zip(headers, col_widths)):
            sheet.write(3, col, h, header_fmt)
            sheet.set_column(col, col, w)
        sheet.set_row(3, 30)

        # ── Data rows ─────────────────────────────────────────────────────────
        for row_idx, rec in enumerate(data, start=4):
            mark = rec.get('mark', 'N')
            sheet.write(row_idx, 0, rec.get('internal_ref') or '', cell_fmt)
            sheet.write(row_idx, 1, rec.get('product_name') or '', cell_fmt)
            sheet.write(row_idx, 2, rec.get('category_name') or '', cell_fmt)
            sheet.write(row_idx, 3, rec.get('location_name') or '', cell_fmt)
            sheet.write(row_idx, 4, float(rec.get('opening_stock') or 0), num_fmt)
            sheet.write(row_idx, 5, float(rec.get('closing_stock') or 0), num_fmt)
            sheet.write(row_idx, 6, float(rec.get('average_stock') or 0), num_fmt)
            sheet.write(row_idx, 7, float(rec.get('sale_qty') or 0), num_fmt)
            sheet.write(row_idx, 8, round(float(rec.get('turnover_ratio') or 0), 4), num_fmt)
            sheet.write(row_idx, 9, mark, mark_fmts.get(mark, cell_fmt))

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read()).decode()

        attachment = self.env['ir.attachment'].create({
            'name': f'FSN_Report_{self.date_start}_{self.date_end}.xlsx',
            'type': 'binary',
            'datas': file_data,
            'mimetype': (
                'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet'
            ),
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
