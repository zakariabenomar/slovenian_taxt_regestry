# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = 'account.tax'

    l10n_si_tax_reg_tax_type = fields.Selection([
            ('regular', 'Regular'),
            ('flat', 'Flat-Rate'),
            ('other', 'Other'),
            ('exempt', 'Tax Exempt'),
            ('reverse', 'Reverse Charge Procedure'),
            ('notax', 'Non-Taxable'),
            ('special', 'Special'),
            ], string='Si. Tax Type', required=True, default='regular')
