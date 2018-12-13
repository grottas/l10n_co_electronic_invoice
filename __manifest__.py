# Copyright <2018> <svazquez@netquest.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Colombia Electronic Invoice',
    'summary': """Electronic invoice for Colombia localization""",
    'description': """Electronic invoice for Colombia localization""",
    'version': '11.0.1.0.0',
    'category': 'account',
    'author': 'Netquest',
    'license': 'AGPL-3',
    'website': 'http://www.netquest.com',
    'contributors': [
        'Susana Vázquez <svazquez@netquest.com>',
    ],
    'depends': [
        'account',

    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_group_data.xml',
        'views/account_invoice.xml',
        'views/account_journal.xml',
        'views/l10n_co_dian_resolution.xml',
        'views/l10n_co_electronic_invoice.xml',
        'views/res_company.xml',

    ],
    'installable': True
}
