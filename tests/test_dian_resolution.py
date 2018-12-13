from odoo import fields

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestL10nCoDianResolution(TransactionCase):

    def setUp(self):
        super(TestL10nCoDianResolution, self).setUp()

        self.dian_resolution = self.env.ref('l10n.co.dian.resolution')
        self.resolution_fe = self.dian_resolution.create({
            'name': 'Resolution FE',
            'document_type': 'fe',
            'technical_key': 'abc123455',
            'prefix': 'PRE',
            'range_from': '1',
            'range_to': '100',
            'next_number': 1,
            'start_date': fields.Date.today(),
            'end_date': fields.Date.today(),
        })







