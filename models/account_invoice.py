from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_co_invoice_electronic_ids = fields.One2many(
        'l10n.co.electronic.invoice',
        'invoice_id',
        'Electronic invoice'
    )
