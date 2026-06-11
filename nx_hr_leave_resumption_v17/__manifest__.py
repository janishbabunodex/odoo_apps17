# -*- coding: utf-8 -*-
{
    'name': 'HR Leave Resumption Date',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Track and manage employee rejoin/resumption date after leave',
    'description': """
        This module extends the HR Leave module to allow tracking of employee
        resumption (rejoin) dates after their approved leave period ends.

        Features:
        - Add a Resumption Date field to leave requests
        - Create a resumption leave record linked to the original leave
        - View resumption leave directly from the leave form
        - Warning notification when resumption date is set
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/hr_employee_views.xml',
        'views/hr_leave_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
