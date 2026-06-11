from odoo import models, fields
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nx_vendor_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)],
        copy=False,
    )
    nx_is_barcode = fields.Boolean(string='Is Barcode', copy=False)

    def generate_product_barcode(self):
        for product in self:
            if product.barcode:
                raise UserError("This product already has a barcode set.")

            if not product.nx_vendor_id:
                raise UserError(
                    "Please select a supplier before generating the product barcode."
                )

            if not product.nx_vendor_id.nx_product_prefix:
                raise UserError(
                    "Selected supplier does not have a Product Prefix. "
                    "Please set it in the supplier form."
                )

            prefix = product.nx_vendor_id.nx_product_prefix.upper()
            sequence = str(product.nx_vendor_id.nx_product_sequence).zfill(5)
            product.barcode = f"{prefix}{sequence}"
            product.nx_vendor_id.nx_product_sequence += 1
            product.nx_is_barcode = True
            product.nx_vendor_id.nx_is_generate = True
