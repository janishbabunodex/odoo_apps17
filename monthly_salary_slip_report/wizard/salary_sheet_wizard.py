import base64
import calendar
from datetime import datetime
from io import BytesIO

import xlsxwriter

from odoo import fields, models


class SalarySheetWizard(models.TransientModel):
    _name = 'salary.sheet.wizard'
    _description = 'Salary Sheet Report Wizard'

    month = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string='Month',
        required=True,
    )

    year = fields.Selection(
        selection='_years_selection',
        string='Year',
        required=True,
    )

    def _years_selection(self):
        current_year = datetime.now().year
        return [
            (str(year), str(year))
            for year in range(current_year - 2, current_year + 10)
        ]

    def action_print_excel_report(self):
        data = {
            'month': int(self.month),
            'year': int(self.year),
        }

        xlsx_bytes = self.env[
            'report.monthly_salary_slip_report.salary_sheet_xlsx'
        ].generate_xlsx(data)

        attachment = self.env['ir.attachment'].create({
            'name': f'Salary Sheet - {self.month}-{self.year}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(xlsx_bytes),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class SalarySheetXlsx(models.TransientModel):
    _name = 'report.monthly_salary_slip_report.salary_sheet_xlsx'
    _description = 'Salary Sheet XLSX Report'

    def generate_xlsx(self, data):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        month = data['month']
        year = data['year']

        sheet = workbook.add_worksheet('Salary Sheet')

        # ---------------------------------------------------------------
        # Formats
        # ---------------------------------------------------------------
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'border': 1,
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2C3E50',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        text_format = workbook.add_format({
            'border': 1,
            'align': 'left',
        })

        center_format = workbook.add_format({
            'border': 1,
            'align': 'center',
        })

        amount_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'align': 'right',
        })

        # ---------------------------------------------------------------
        # Get Payslips
        # ---------------------------------------------------------------
        start_date = f'{year}-{month:02d}-01'
        end_date = f'{year}-{month:02d}-{calendar.monthrange(year, month)[1]}'

        payslips = self.env['hr.payslip'].search([
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),
            ('state', '=', 'done'),
        ])

        # ---------------------------------------------------------------
        # Dynamic Salary Components
        # ---------------------------------------------------------------
        component_names = payslips.mapped('line_ids.name')
        unique_components = sorted(set(component_names))

        # Move Gross & Net Salary to the end
        for item in ['Gross', 'Net Salary']:
            if item in unique_components:
                unique_components.remove(item)
                unique_components.append(item)

        headers = [
            'SL',
            'EMPLOYEE NAME',
            'EMPLOYEE CODE',
            'DEPARTMENT',
        ] + unique_components

        # ---------------------------------------------------------------
        # Report Title
        # ---------------------------------------------------------------
        month_name = calendar.month_name[month]

        sheet.merge_range(
            0, 0, 0, len(headers) - 1,
            f'Salary Sheet - {month_name} {year}',
            title_format,
        )

        # ---------------------------------------------------------------
        # Header Row
        # ---------------------------------------------------------------
        header_row = 2

        for col, header in enumerate(headers):
            sheet.write(header_row, col, header, header_format)

        sheet.freeze_panes(header_row + 1, 4)

        # ---------------------------------------------------------------
        # Employee Data
        # ---------------------------------------------------------------
        row = header_row + 1
        sl_no = 1

        for slip in payslips:
            col = 0

            # SL
            sheet.write(row, col, sl_no, center_format)
            col += 1

            # Employee Name
            sheet.write(row, col, slip.employee_id.name or '', text_format)
            col += 1

            # Employee Code
            employee_code = (
                getattr(slip.employee_id, 'employee_code', False)
                or slip.employee_id.barcode
                or ''
            )
            sheet.write(row, col, employee_code, text_format)
            col += 1

            # Department
            sheet.write(
                row, col,
                slip.employee_id.department_id.name or '',
                text_format,
            )
            col += 1

            # Salary Component Values
            line_dict = {line.name: line.total for line in slip.line_ids}

            for component in unique_components:
                sheet.write(
                    row, col,
                    line_dict.get(component, 0.0),
                    amount_format,
                )
                col += 1

            row += 1
            sl_no += 1

        # ---------------------------------------------------------------
        # Column Widths
        # ---------------------------------------------------------------
        sheet.set_column(0, 0, 8)    # SL
        sheet.set_column(1, 1, 30)   # Employee Name
        sheet.set_column(2, 2, 20)   # Employee Code
        sheet.set_column(3, 3, 25)   # Department

        for col in range(4, len(headers)):
            sheet.set_column(col, col, 18)

        workbook.close()
        output.seek(0)

        return output.read()
