# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class L10nSiTaxRegVat(models.TransientModel):
    _name = 'l10n_si_tax_reg.vat'
    _description = 'Si. Tax Reg. VAT'

    name = fields.Char(string='TIN', size=8, required=True)

    def action_assign_vat(self):
        ids = self.env.context.get('active_ids', False)
        if not ids:
            return True
        partner = self.env['res.partner'].browse(ids)
        for vat in self:
            partner.write({'vat': 'SI' + vat.name})

        return True
