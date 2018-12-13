from odoo import fields, api, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_co_dian_enabled = fields.Boolean('DIAN - Electronic invoice')
    l10n_co_dian_id = fields.Char('DIAN id')
    l10n_co_software_id = fields.Char('Software Id')
    l10n_co_pin = fields.Char('PIN')
    l10n_co_password = fields.Char('Password')
    l10n_co_service_provider = fields.Selection([
        ('dian_cert', 'DIAN - Certification process'),
        ('dian', 'DIAN'),
    ], string='Service Provider')
