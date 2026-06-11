# -*- coding: utf-8 -*-
{
    'name': 'HR Leave Resumption Date',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Track employee resumption (rejoin) date after approved leave',
    'description': """
HR Leave Resumption Date
========================

This module extends Odoo's HR Leave (Time Off) module to track and manage
employee resumption (rejoin) dates after approved leave periods.

Key Features
------------
* **Resumption Date field** on leave requests — record the expected return-to-work date
* **Validation** — resumption date cannot be earlier than the leave end date
* **Create Resumption Leave** button — automatically creates a linked leave record for the resumption day (visible only after leave is validated)
* **View Resumption Leave** smart button — jump directly to the linked resumption record
* **Rejoin Date on Employee** — store the employee's actual rejoin date with full tracking
* **Flight Ticket Eligible Date** — automatically computed as two years after the rejoin date
* Full chatter tracking on all new fields

Compatibility
-------------
* Odoo 17.0 Community & Enterprise
* Depends on: hr_holidays

License: LGPL-3
    """,
    'author': 'Nxtech Solutions',
    'website': 'https://www.nxtechsolutions.com',
    'support': 'support@nxtechsolutions.com',
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
    ],
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
    'price': 0,
    'currency': 'USD',
}
