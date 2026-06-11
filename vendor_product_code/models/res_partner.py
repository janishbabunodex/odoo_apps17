import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    nx_product_prefix = fields.Char(string='Product Prefix')
    nx_product_sequence = fields.Integer(string='Product Sequence', default=1)
    nx_is_generate = fields.Boolean(string='Is Generate', copy=False)

    @api.constrains('nx_product_prefix')
    def _check_nx_product_prefix(self):
        for rec in self:
            if rec.nx_product_prefix:
                if not re.fullmatch(r'^[A-Za-z0-9]{4}$', rec.nx_product_prefix):
                    raise ValidationError(
                        "Product Prefix must contain exactly 4 alphanumeric characters (A–Z, 0–9)."
                    )
