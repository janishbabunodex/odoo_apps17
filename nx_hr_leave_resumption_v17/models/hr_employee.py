from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    nx_rejoin_date = fields.Date(string='Rejoin Date',tracking=True)
    nx_ticket_eligible = fields.Date(
        string='Flight Eligible Date',
        compute='_compute_ticket_eligible',
        store=True
    )

    @api.depends('nx_rejoin_date')
    def _compute_ticket_eligible(self):
        for rec in self:
            if rec.nx_rejoin_date:
                rec.nx_ticket_eligible = rec.nx_rejoin_date + relativedelta(years=2)
            else:
                rec.nx_ticket_eligible = False
