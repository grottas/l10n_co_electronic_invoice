from odoo import api, fields, models


class AccountJournalDianResolutions(models.Model):
    _name = "account.journal.dian.resolutions"

    l10n_co_dian_resolution_id = fields.Many2one(
        'l10n.co.dian.resolution',
        'DIAN Resolution',
        ondelete='cascade',
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        ondelete='cascade',
    )


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_co_journal_resolution_ids = fields.One2many(
        'account.journal.dian.resolutions',
        'journal_id',
        'DIAN - Resolutions')
