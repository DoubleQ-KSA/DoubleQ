from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    po_type = fields.Char(string="Type")