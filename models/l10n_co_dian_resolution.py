from odoo import api, fields, models


class L10nCoDianResolution(models.Model):
    _name = "l10n.co.dian.resolution"

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    document_type = fields.Selection([
        ('fe', 'Electronic Invoice'),
        ('nd', 'Debit note'),
        ('nc', 'Credit note')
    ], string='Document Type', required=True, default='fe')
    resolution_number = fields.Char(string='Resolution Number', required=True)
    technical_key = fields.Char(string='Technical Key', required=True)
    prefix = fields.Char('Prefix')
    range_from = fields.Integer('Range From', required=True)
    range_to = fields.Integer('Range To', required=True)
    next_number = fields.Integer('Next Number', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    active = fields.Boolean('Active', default=True)
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 ondelete='cascade')
