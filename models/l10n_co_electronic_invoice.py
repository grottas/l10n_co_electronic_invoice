import datetime
import hashlib
import logging
import os
import re
import requests
import pytz

from jinja2 import Environment, FileSystemLoader
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


server_url = {
    'OPERACION': 'https://facturaelectronica.dian.gov.co/operacion/B2BIntegrationEngine/FacturaElectronica/facturaElectronica.wsdl',
    'HABILITACION':'https://facturaelectronica.dian.gov.co/habilitacion/B2BIntegrationEngine/FacturaElectronica/facturaElectronica.wsdl',
}


class L10nCoElectronicInvoice(models.Model):
    _name = 'l10n.co.electronic.invoice'

    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    invoice_time = fields.Char(compute='_get_co_current_datetime',
                               string='Invoice Time', readonly=True)
    send_date = fields.Date('Send Date')
    request_send = fields.Char('Request Send')
    response_code = fields.Char('Response Code')
    validation_date = fields.Date('Validation Date')
    validation_response = fields.Char('Validation Response')
    validation_response_code = fields.Char('Validation Response Code')
    qr_code = fields.Binary('QR code', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('error', 'Error'),
         ('done', 'Send'),
         ('cancel', 'Cancel')],
        string='State', default='draft', readonly=True)

    def _hook_validation(self):
        errors = []
        # TODO required fields for Colombian electronic invoices
        # Company
        if not self.company_id.partner_id.vat:
            errors.append('Company - NIT')
        if not self.company_id.partner_id.city:
            errors.append('Company Partner - City')
        if not self.company_id.partner_id.street:
            errors.append('Company Partner - Street')
        if not self.company_id.partner_id.country_id:
            errors.append('Company Partner - Country')
        # Partner
        if not self.invoice_id.partner_id.vat:
            errors.append('Partner - VAT')
        # if not self.invoice_id.partner_id.city:
        #     errors.append('Partner - City')
        if not self.invoice_id.partner_id.street:
            errors.append('Partner - Street')
        if not self.invoice_id.partner_id.country_id:
            errors.append('Partner - Country')

        # Products

        return errors

    def _get_invoice_type(self):
        types = {
            'out_invoice': ('f', 'Invoice'),
            'in_invoice': ('f', 'Invoice'),
            'out_refund': ('c', 'CreditNote'),
            'in_refund': ('d', 'DebitNote'),
        }
        return types.get(self.invoice_id.type)

    @staticmethod
    def _get_format_vat(vat):
        vat = ''.join(list(filter(str.isdigit, vat)))
        return vat.rjust(10, '0')

    def _get_invoice_number(self):
        invoice = self.invoice_id
        prefix, suffix = invoice.journal_id.sequence_id._get_prefix_suffix()
        seq_number = re.sub(prefix or '', '',
                            re.sub(suffix or '', '', invoice.number))
        return seq_number

    def _get_hex(self):
        return format(int(self._get_invoice_number()), 'x').rjust(10, '0')

    def _get_file_name(self):
        file_name = '%s_%s%s%s' % (
            'face',
            self._get_invoice_type()[0],
            self._get_format_vat(self.invoice_id.company_id.partner_id.vat),
            self._get_hex()
        )
        return file_name

    @staticmethod
    def _get_co_current_datetime():
        tz = pytz.timezone('America/Bogota')
        return datetime.datetime.now(tz=tz)

    def _get_format_current_date(self, format_date="%Y-%m-%dT%H:%M:%S"):
        return self._get_co_current_datetime().strftime(format_date)

    @staticmethod
    def _change_date_format(date, format_date="%Y-%m-%dT%H:%M:%S"):
        datetime_date = fields.Date.from_string(date)
        return datetime_date.strftime(format_date)

    @staticmethod
    def _get_template_xml(values, template_name):
        base_path = os.path.dirname(os.path.dirname(__file__))
        env = Environment(
            loader=FileSystemLoader(
                os.path.join(base_path, 'template')))
        template = env.get_template('{}.xml'.format(template_name))
        xml = template.render(values)
        xml = xml.replace('&', '&amp;')
        return xml

    # TODO
    def _get_invoice_type_code(self):
        invoice_type_code = {
            1: 'Factura de Venta',
            2: 'Factura de Exportación',
            3: 'Factura de Contingecia'
        }
        return 1

    def _prepare_cufe_values(self, technical_key):
        NumFac = self.invoice_id.number
        FecFac = self._change_date_format(self.invoice_id.date, "%Y%m%dT%H%M%S")
        ValFac = str(self.invoice_id.amount_untaxed)
        CodImp1 = '01'
        ValImp1 = ''
        CodImp2 = '02'
        ValImp2 = ''
        CodImp3 = '03'
        ValImp3 = ''
        ValImp = str(self.invoice_id.amount_tax)
        NitOFE = self._get_format_vat(self.company_id.partner_id.vat)
        TipAdq = ''
        NumAdq = self._get_format_vat(self.invoice_id.partner_id.vat)
        ClTec = technical_key

        return ''.join([NumFac, FecFac, ValFac,CodImp1, ValImp1, CodImp2,
                        ValImp2, CodImp3, ValImp3, ValImp, NitOFE, TipAdq,
                        NumAdq, ClTec])

    def _cufe_generator(self, technical_key):
        if self._get_invoice_type_code() not in (1, 2):
            return

        values = self._prepare_cufe_values(technical_key)
        cufe = hashlib.sha1(values.encode('utf-8'))
        return cufe.hexdigest()

    def _prepare_party_legal_entity(self):
        return {
            'CorporateRegistrationScheme': {
                'CorporateRegistrationTypeCode': '',
            }
        }

    def _prepare_accounting_supplier_party_values(self):
        supplier = self.company_id.partner_id \
            if self.invoice_id.type in ('out_invoice', 'out_refund') \
            else self.invoice_id.partner_id

        return {
            'AdditionalAccountID': '2' if supplier.company_type == 'company'
            else '1',
            'PartyTaxScheme': '',
            'PartyLegalEntity': '',
            'ID': supplier.vat,
            'Name': supplier.name,
            'CityName': supplier.city,
            'Line': supplier.street,
            'IdentificationCode': supplier.country_id.code,
            'TaxLevelCode': 'TODO',
            'TaxSchemaName': 'TODO',
            'RegistrationName': supplier.vat,
        }

    def _prepare_accounting_customer_party_values(self):
        customer = self.company_id.partner_id \
            if self.invoice_id.type in ('in_invoice', 'in_refund') \
            else self.invoice_id.partner_id

        return {
            'AdditionalAccountID': '2' if customer.company_type == 'company' else '1',
            'ID': customer.vat,
            'TaxLevelCode': 'TODO',
            'TaxSchemaName': 'TODO',
        }

    def _prepare_xml_values(self):
        # dian_resolution = self.invoice_id.journal_id.l10n_co_dian_resolution
        dian_resolution = self.env['l10n.co.dian.resolution'].browse(1)
        values = {
            'DocumentType': self._get_invoice_type(),
            'InvoiceAuthorization': dian_resolution.resolution_number,
            'StartDate': dian_resolution.start_date,
            'EndDate': dian_resolution.end_date,
            'Prefix': dian_resolution.prefix,
            'From': dian_resolution.range_from,
            'To': dian_resolution.range_to,
            'ProviderID': self.company_id.partner_id.vat,
            'SoftwareID': self.company_id.l10n_co_software_id,
            'SoftwareSecurityCode': 'TODO',
            'ID': self.invoice_id.number,
            'UUID': self._cufe_generator(dian_resolution.technical_key),
            'IssueDate': self.invoice_id.date_invoice,
            'IssueTime': self.invoice_time,
            'InvoiceTypeCode': self._get_invoice_type_code(),
            'DocumentCurrencyCode': self.invoice_id.currency_id.name,
            'AccountingSupplierParty':
                self._prepare_accounting_supplier_party_values(),
            'AccountingCustomerParty':
                self._prepare_accounting_customer_party_values(),
        }

        return values

    def _get_xml_without_sing(self):
        values = self._prepare_xml_values()
        return self._get_template_xml(values, 'dian')

    def _get_signature(self, xml_without_signed):
        digest1 = hashlib.sha256(self.xml_without_signed.encode())
        print(digest1.hexdigest())
        values = {
            'Id': '',
            'data_xml_signature_ref_zero': '',
            'data_public_certificate_base': '',
            'data_xml_keyinfo_base': '',
            'data_xml_politics': '',
            'data_xml_SignedProperties_base': '',
            'signing_time': self._get_format_current_date(),
            'DigestValue': '',
            'IssuerName': '',
            'SerialNumber': '',
            'IdSignature': '',
            'IdReference_zero': '',
            'URIReference_keyinfo': '',
            'URIReference_signedprops': '',
            'IdSignatureValue': '',
            'IdKeyInfo': '',
            'IdSignedProperties': '',
            'Target': '',
            'SignatureValue': '',
        }
        return self._get_template_xml(values, 'signature')

    def _create_xml(self):
        xml_without_signed = self._get_xml_without_sing()
        signature = self._get_signature(xml_without_signed)
        xml_signed = signature + xml_without_signed
        print(xml_without_signed)
        return xml_without_signed

    def _get_server_url(self):
        service_provider = self.company_id.l10n_co_service_provider
        return server_url['OPERACION'] if service_provider == 'dian' \
            else server_url['HABILITACION']

    def _action_send_xml(self):
        # file_name = self._get_file_name()
        header = {'content-type': 'text/xml'}
        try:
            response = requests.post(self._get_server_url(),
                                     data=self.request_send,
                                     headers=header)
            # self.response_code = 0
            self.send_date = self._get_co_current_datetime()
            print(response)
        except Exception as e:
            print(e)
            _logger.error('DIAN Error', exc_info=True)

    @api.multi
    def action_post_validate(self):
        self.request_send = self._create_xml()
        self._action_send_xml()

    @api.multi
    def validate_invoice(self):
        self.ensure_one()
        errors = self._hook_validation()
        if len(errors) > 0:
            raise UserError("Please set values of following fields %s "
                            % errors)

    @api.multi
    def action_cancel(self):
        pass

    @api.multi
    def action_back_to_draft(self):
        pass

    @api.model
    def create(self, vals):
        vals['invoice_time'] = self._change_date_format(
            fields.Date.to_string(self._get_co_current_datetime()),
            "%H:%M:%S"
        )
        return super(L10nCoElectronicInvoice, self).create(vals)
