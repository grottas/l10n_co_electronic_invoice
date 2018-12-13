# © 2018 Susana Vázquez <svazquez@netquest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_co_invoice_electronic_ids = fields.One2many(
        'l10n.co.electronic.invoice',
        'invoice_id',
        'Electronic invoice'
    )

    def _prepare_einvoice_vals(self):
        return {
            'invoice_id': self.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self.filtered(lambda x: x.company_id.l10n_co_dian_enabled):
            einv_vals = self._prepare_einvoice_vals()
            einv = self.env['l10n.co.electronic.invoice'].create(einv_vals)
            einv.validate_invoice()
            einv.action_post_validate()

        return res

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        for inv in self.filtered(lambda x: x.l10n_co_dian_enabled):
            invoice_sent_dian = inv.filtered(
                lambda x: x.l10n_co_invoice_electronic_ids.state == 'done')

            if invoice_sent_dian:
                raise UserError('Can\'t cancel invoice sent to DIAN')

        return res


