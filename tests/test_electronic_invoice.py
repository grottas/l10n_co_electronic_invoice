import mock

from odoo import fields

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestL10nCoElectronicInvoice(TransactionCase):

    def setUp(self):
        super(TestL10nCoElectronicInvoice, self).setUp()

        self.l10n_co_einvoice = self.env['l10n.co.electronic.invoice']
        self.main_company = self.env.ref('base.main_company')
        self.currency = self.env.ref('base.COP')

        self.receivable_account = self.env['account.account'].create(dict(
            code='10000000',
            name='Account test',
            reconcile=True,
            user_type_id=self.env.ref(
                'account.data_account_type_receivable').id,
            company_id=self.main_company.id,
        ))

        self.partner = self.env['res.partner'].create(dict(
            name='PartnerTest',
            company_type='company',
            vat='8355990',
            is_company=True,
            property_account_receivable_id=self.receivable_account.id,
        ))

        self.product = self.env['product.product'].create(dict(
            name='Product test',
        ))

        self.journal = self.env['account.journal'].create(dict(
            name='Journal Test',
            code='FE',
            type='sale',
            default_debit_account_id=self.receivable_account.id,
            default_credit_account_id=self.receivable_account.id,
        ))

        invoice_line = [
            (0, 0,
             {
                 'product_id': self.product.id,
                 'quantity': 10.0,
                 'account_id': self.receivable_account.id,
                 'name': 'product test',
                 'price_unit': 10,
             }
             )
        ]

        self.invoice = self.env['account.invoice'].create(dict(
            name='Invoice Test',
            journal_id=self.journal.id,
            partner_id=self.partner.id,
            account_id=self.receivable_account.id,
            invoice_line_ids=invoice_line,
        ))

        self.electronic_invoice = self.l10n_co_einvoice.create(dict(
            invoice_id=self.invoice.id,
            company_id=self.main_company.id,
        ))

    def test_get_file_name(self):
        self.main_company.vat = '98765432'
        self.invoice.action_invoice_open()
        file_name = self.electronic_invoice._get_file_name()

        self.assertEquals(len(file_name), 26)
        self.assertEquals(file_name, 'face_f00987654320000000001')

    def test_create_electronic_invoice(self):
        einvoice = self.l10n_co_einvoice.create(dict(
            invoice_id=self.invoice.id,
            company_id=self.main_company.id,
        ))

        self.assertTrue(einvoice)
        self.assertEqual(einvoice.invoice_id.id, self.invoice.id)
        self.assertEqual(einvoice.company_id.id, self.invoice.company_id.id)

    # def test_prepare_cufe_values(self):
    #     res = self.l10n_co_einvoice._prepare_cufe_values(
    #         '693ff6f2a553c3646a063436fd4dd9ded0311471')
    #
    #     self.assertEqual(res, ('323200000129201508120611311109376.00010.'
    #                            '000245928.1603107165.721296705.207000853'
    #                            '7131800199436693ff6f2a553c3646a063436fd4'
    #                            'dd9ded0311471'))

    @mock.patch('odoo.addons.l10n_co_electronic_invoice.models.l10n_co_electronic_invoice.L10nCoElectronicInvoice._prepare_cufe_values')  # noqa
    def test_cufe_generator(self, cufe_values):
        def _prepare_cufe_values(technical_key):
            return ('323200000129201508120611311109376.00010.000245928.' 
                    '1603107165.721296705.2070008537131800199436693ff6f2'
                    'a553c3646a063436fd4dd9ded0311471')

        cufe_values.side_effect = _prepare_cufe_values
        res = self.l10n_co_einvoice._cufe_generator('')

        self.assertEqual(res, '77c35e565a8d8f9178f2c0cb422b067091c1d760')










