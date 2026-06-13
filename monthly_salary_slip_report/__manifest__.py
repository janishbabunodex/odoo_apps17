{
    'name': 'Monthly Salary Slip Report',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Generate a monthly salary sheet report in Excel for all employees',
    'description': """
Monthly Salary Slip Report
===========================

Generate a consolidated, ready-to-print **Monthly Salary Sheet** in Excel
format for all employees, directly from the Payroll module.

Key Features
------------
* Select **Month and Year** from a simple wizard.
* Generates an **Excel (.xlsx)** report listing all confirmed (done) payslips
  for the selected month.
* Dynamic columns — automatically includes every salary rule/component used
  across the selected payslips (Basic, Allowances, Deductions, etc.).
* **Gross** and **Net Salary** columns are always placed at the end for
  quick reference.
* Includes Employee Name, Employee Code, and Department for each row.
* Professional formatting with styled headers and auto-sized columns.
* One-click download — no manual setup or templates required.

Use Case
--------
HR and Payroll teams who need a single consolidated salary sheet for payroll
review, bank transfer processing, or auditing purposes.
    """,
    'author': 'Nodex Technologies LLC',
    'company': 'Nodex Technologies LLC',
    'maintainer': 'Nodex Technologies LLC',
    'website': 'https://www.nodex.ae',
    'depends': ['hr_payroll_community'],
    'data': [
        'security/ir.model.access.csv',
        'views/salary_sheet_wizard_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
