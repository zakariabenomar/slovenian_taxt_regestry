# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

from . l10n_si_tax_reg_premise import INVALID_FORMAT_MSG

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    l10n_si_tax_reg_has_premise = fields.Boolean(string='Is a Slovenian Tax Registry Business Premise', compute='_compute_l10n_si_tax_reg_has_premise')
    l10n_si_tax_reg_vat = fields.Char(string='TIN for Si. Tax Reg', compute='_compute_l10n_si_tax_reg_vat')

    def _compute_l10n_si_tax_reg_has_premise(self):
        ids = [x.id for x in self]
        if not ids:
            for partner in self:
                partner.l10n_si_tax_reg_has_premise = False
            return

        self.env.cr.execute('SELECT res_partner_id FROM ' + self.env['l10n_si_tax_reg.premise']._table +
            ' WHERE res_partner_id IN %s', (tuple(ids),))
        res_ids = [row[0] for row in self.env.cr.fetchall()]
        for partner in self:
            partner.l10n_si_tax_reg_has_premise = True if partner.id in res_ids else False

    def _compute_l10n_si_tax_reg_vat(self):
        for partner in self:
            partner.l10n_si_tax_reg_vat = partner.vat and partner.vat.lstrip('SI') or ''

    @api.constrains('name')
    def _check_name(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if not re.match('^[0-9a-zA-Z]{1,20}$', partner.name):
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('name'))
            if self.env['l10n_si_tax_reg.premise'].search_count([('res_partner_id', '<>', partner.id), ('name', '=', partner.name)]) > 0:
                raise exceptions.ValidationError(_('Business premise with this name already exists!'))

    @api.constrains('comment')
    def _check_comment(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if partner.comment and len(partner.comment) > 1000:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('comment'))

    @api.constrains('street')
    def _check_street(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if not re.match('^.{1,100} [0-9]{1,10}.{0,10}$', partner.street):
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('street'))

    @api.constrains('street2')
    def _check_street2(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if not partner.street2:
                continue

            if len(partner.street2) > 100:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('street2'))

    @api.constrains('zip')
    def _check_zip(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if len(partner.zip) != 4:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('zip'))

    @api.constrains('city')
    def _check_city(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if len(partner.city) > 40:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('city'))

    @api.constrains('company_id')
    def _check_company_id(self):
        for partner in self:
            if not partner.l10n_si_tax_reg_has_premise:
                continue

            if not partner.company_id.vat or not re.match('^(SI)?[0-9]{8}$', partner.company_id.vat):
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('company vat'))
