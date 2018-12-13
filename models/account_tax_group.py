from odoo import api, fields, models


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    l10n_co_dian_code = fields.Integer(
        'Dian Code'
    )
