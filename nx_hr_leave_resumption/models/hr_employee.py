# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    nx_rejoin_date = fields.Date(
        string='Rejoin Date',
        tracking=True,
        help="The date the employee officially rejoined work after their leave.",
    )
    nx_ticket_eligible = fields.Date(
        string='Flight Ticket Eligible Date',
        compute='_compute_ticket_eligible',
        store=True,
        help="Automatically computed as two years after the rejoin date.",
    )

    @api.depends('nx_rejoin_date')
    def _compute_ticket_eligible(self):
        for rec in self:
            rec.nx_ticket_eligible = (
                rec.nx_rejoin_date + relativedelta(years=2)
                if rec.nx_rejoin_date
                else False
            )
