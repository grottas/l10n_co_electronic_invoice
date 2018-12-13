from odoo import api, fields, models


class L10nCoElectronicInvoice(models.Model):
    _name = 'l10n.co.electronic.invoice'

    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', readonly=True)
    send_date = fields.Date('Send Date')
    request_send = fields.Date('Request Send')
    response_code = fields.Char('Response Code')
    validation_date = fields.Date('Validation Date')
    validation_response = fields.Char('Validation Response')
    validation_response_code = fields.Char('Validation Response Code')
