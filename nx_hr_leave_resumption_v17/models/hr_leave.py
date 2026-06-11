# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    resumption_date = fields.Date(
        string='Resumption Date',
        tracking=True,
        help="The date the employee is expected to resume/rejoin work after this leave.",
    )
    nx_resumption_leave_id = fields.Many2one(
        comodel_name='hr.leave',
        string='Resumption Leave',
        readonly=True,
        copy=False,
        ondelete='set null',
        help="The linked resumption leave record created for this leave.",
    )
    has_resumption_leave = fields.Boolean(
        string='Has Resumption Leave',
        compute='_compute_has_resumption_leave',
        store=False,
    )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------
    @api.depends('nx_resumption_leave_id')
    def _compute_has_resumption_leave(self):
        for rec in self:
            rec.has_resumption_leave = bool(rec.nx_resumption_leave_id)

    # -------------------------------------------------------------------------
    # Onchange Methods
    # -------------------------------------------------------------------------
    @api.onchange('resumption_date')
    def _onchange_resumption_date(self):
        for rec in self:
            if rec.resumption_date and rec.request_date_to:
                return {
                    'warning': {
                        'title': _('Employee Resumption Date Confirmation'),
                        'message': _(
                            "Employee '%s' has a resumption date matching the last leave date '%s'.\n\n"
                            "Do you want to continue?"
                        ) % (
                                       rec.employee_id.name,
                                       rec.resumption_date.strftime('%d-%m-%Y') if rec.resumption_date else ''
                                   )
                    }
                }

    # -------------------------------------------------------------------------
    # Constraint Methods
    # -------------------------------------------------------------------------
    @api.constrains('resumption_date', 'request_date_to')
    def _check_resumption_date(self):
        """Ensure resumption date is not before the leave end date."""
        for rec in self:
            if rec.resumption_date and rec.request_date_to:
                if rec.resumption_date < rec.request_date_to:
                    raise ValidationError(_(
                        "Resumption Date (%s) cannot be earlier than the Leave End Date (%s) "
                        "for employee '%s'."
                    ) % (
                        rec.resumption_date.strftime('%d-%m-%Y'),
                        rec.request_date_to.strftime('%d-%m-%Y'),
                        rec.employee_id.name,
                    ))

    # -------------------------------------------------------------------------
    # Action Methods
    # -------------------------------------------------------------------------
    def create_resumption_leave(self):
        """
        Create a linked resumption leave record for this leave request.
        The resumption leave is recorded on the resumption_date as a single-day entry.
        """
        self.ensure_one()

        if not self.resumption_date:
            raise UserError(_("Please set a Resumption Date before creating a resumption leave."))

        if self.nx_resumption_leave_id:
            raise UserError(_(
                "A resumption leave already exists for this record: %s.\n"
                "Use the 'View Resumption' button to open it."
            ) % self.nx_resumption_leave_id.name)

        # Resolve the unpaid leave type; raise a clear error if not found.
        try:
            holiday_status = self.env.ref('hr_holidays.holiday_status_unpaid')
        except ValueError:
            raise UserError(_(
                "The default 'Unpaid' leave type could not be found. "
                "Please configure a leave type for resumptions."
            ))

        leave = self.env['hr.leave'].sudo().create({
            'employee_id': self.employee_id.id,
            'name': _('Resumption - %s') % (self.name or self.display_name),
            'request_date_from': (
                self.resumption_date
                if self.request_date_to + timedelta(days=1) == self.resumption_date
                else self.request_date_to + timedelta(days=1)
            ),
            'request_date_to': self.resumption_date,
            'holiday_status_id': holiday_status.id,
            'state': 'draft',
        })

        self.nx_resumption_leave_id = leave.id

        return {
            'name': _('Resumption Leave'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'form',
            'target': 'current',
            'res_id': leave.id,
            'context': {
                'create': False,
            },
        }

    def action_view_resumption(self):
        """Open the linked resumption leave form view."""
        self.ensure_one()

        if not self.nx_resumption_leave_id:
            raise UserError(_("No resumption leave is linked to this record yet."))

        return {
            'name': _('Resumption Leave'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.nx_resumption_leave_id.id,
            'context': {
                'create': False,
            },
        }
