# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

from .. SITaxReg.SITaxReg import SITaxReg
from .. TmpCert.TmpCert import TmpCert

INVALID_FORMAT_MSG = _('Invalid format for "%s"!')

class L10nSiTaxRegPremise(models.Model):
    _name = 'l10n_si_tax_reg.premise'
    _description = 'Business Premise'
    _inherit = ['mail.thread']
    _sql_constraints = [
        ('res_partner_id_uniq', 'UNIQUE(res_partner_id)', 'This contact address already has a business premise!'),
        ('ir_sequence_id_uniq', 'UNIQUE(ir_sequence_id)', 'This invoice numbering sequence has already been set on another premise!'),
    ]

    name = fields.Char(string='Name', size=20, required=True, related='res_partner_id.name',
        help='Business premise ID.')
    res_partner_id = fields.Many2one('res.partner', string='Related Address', readonly=True, states={'draft': [('readonly', False)]}, ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Invoice Issuer', required=True, related='res_partner_id.company_id',
        default=lambda self: self.env['res.company']._company_default_get('account.move'), help='Person liable for invoice issue.')
    partner_id = fields.Many2one('res.partner', string='Software Maintainer', required=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='restrict',
        help='Producer or software maintenance provider.')
    ir_sequence_id = fields.Many2one('ir.sequence', string='Invoice Numbering Sequence', ondelete='set null',
        help='If invoice numbering method is set at the level of business premises, set the numbering sequence for this premise here.')
    l10n_si_tax_reg_premise_line_ids = fields.One2many('l10n_si_tax_reg.premise.line', 'l10n_si_tax_reg_premise_id', string='Electronic Devices')

    date = fields.Date(string='Valid Date', required=True, related='res_partner_id.date',
        help='Premise valid start date.')
    state = fields.Selection([
            ('draft', 'New'),
            ('done', 'Registered'),
            ('cancel', 'Closed'),
            ], string='Operational', required=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'New' status is used when we are preparing a new business location for registration.\n"
             " * The 'Registered' status is used when the premise has been confirmed and successfully registered at the tax registry.\n"
             " * The 'Closed' status is used when the premise is no longer in operation and its closure has been reported to the tax registry.")

    type = fields.Selection([
            ('real_estate', 'Real Estate'),
            ('movable', 'Movable'),
            ], string='Premise Type', required=True, default='real_estate', readonly=True, states={'draft': [('readonly', False)]})
    type_movable = fields.Selection([
            ('a', 'Mobile'),
            ('b', 'Stationary'),
            ('c', 'Other'),
            ], string='Movable Type', readonly=True, states={'draft': [('readonly', False)]},
        help=" * 'Mobile' - movable object such as a vehicle or movable stand.\n"
             " * 'Stationary' - object at a permanent location (e.g. market or news stand).\n"
             " * 'Other' - No other available business premise used for issuing invoices.")
    number_cadastral = fields.Integer(string='Cadastral Number', readonly=True, states={'draft': [('readonly', False)]})
    number_building = fields.Integer(string='Building Number', readonly=True, states={'draft': [('readonly', False)]})
    number_section_building = fields.Integer(string='Part Number of Building', readonly=True, states={'draft': [('readonly', False)]})
    street = fields.Char(size=120, related='res_partner_id.street')
    street2 = fields.Char(string='Community', size=100, related='res_partner_id.street2')
    city = fields.Char(size=40, related='res_partner_id.city')
    zip = fields.Char(size=4, related='res_partner_id.zip')

    comment = fields.Text(related='res_partner_id.comment')

    @api.constrains('res_partner_id')
    def _check_res_partner_id(self):
        for partner in self:
            if not partner.res_partner_id:
                raise exceptions.ValidationError(_('Related address cannot be removed once the premise has been created!'))

    # TODO: preveri ali imajo for zanke continue

    @api.constrains('partner_id')
    def _check_partner_id(self):
        for premise in self:
            if not premise.partner_id.country_id:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('software maintainer'))

            if premise.partner_id.country_id.code.upper().encode('UTF-8') == 'SI':
                if not premise.partner_id.vat or not re.match('^(SI)?[0-9]{8}$', premise.partner_id.vat):
                    raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('software maintainer'))
            elif not premise.partner_id.street or not premise.partner_id.city or not premise.partner_id.zip:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('software maintainer'))

    @api.constrains('ir_sequence_id')
    def _check_ir_sequence_id(self):
        for premise in self:
            if not len(premise.l10n_si_tax_reg_premise_line_ids) or premise.ir_sequence_id:
                continue

            for line in premise.l10n_si_tax_reg_premise_line_ids:
                if not line.ir_sequence_id:
                    raise exceptions.ValidationError(_('Either business premise or all its electronic devices (or both) must have invoice numbering sequence set.'))

    @api.constrains('type')
    def _check_type(self):
        for premise in self:
            if premise.type == 'real_estate':
                if not premise.number_cadastral or not premise.number_building or not premise.number_section_building or \
                        not premise.street or not premise.street2 or not premise.city or not premise.zip:
                    raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('type'))
            elif premise.type == 'movable' and not premise.type_movable:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('type'))

    @api.constrains('number_cadastral')
    def _check_number_cadastral(self):
        for premise in self:
            if premise.number_cadastral > 9999 or premise.number_cadastral < 0:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('cadastral'))

    @api.constrains('number_building')
    def _check_number_building(self):
        for premise in self:
            if premise.number_building > 99999 or premise.number_building < 0:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('number'))

    @api.constrains('number_section_building')
    def _check_number_section_building(self):
        for premise in self:
            if premise.number_section_building > 9999 or premise.number_section_building < 0:
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('part'))

    @api.model
    def create(self, vals):
        if vals.get('res_partner_id', False):
            return super(L10nSiTaxRegPremise, self).create(vals)

        partner_vals = {
            'country_id': self.env.ref('base.si').id,
            'customer': False,
        }
        for val in ['name', 'date', 'street', 'street2', 'city', 'zip', 'comment']:
            if val in vals:
                partner_vals[val] = vals[val]
        partner = self.env['res.partner'].create(partner_vals)
        vals.update({'res_partner_id': partner.id})
        return super(L10nSiTaxRegPremise, self).create(vals)

    def unlink(self):
        for premise in self:
            if premise.state == 'done':
                raise exceptions.Warning(_('You cannot delete registered business premises. You should close it first.'))
        return super(L10nSiTaxRegPremise, self).unlink()

    def action_done(self):
        t = TmpCert()
        try:
            for premise in self:
                certs = t.record_open_write(premise.company_id)
                s = SITaxReg(certs[0], certs[1], ca_certs=certs[2], dev=premise.company_id.l10n_si_tax_reg_dev)
                data = premise.with_context(closure=False)._get_export_for_registry()
                if not s.register_business_premise(data):
                    raise exceptions.Warning(_('Registry server did not return expected response.'))

                premise.state = 'done'
        finally:
            t.rmtree()

        return True

    def action_cancel(self):
        t = TmpCert()
        try:
            for premise in self:
                certs = t.record_open_write(premise.company_id)
                s = SITaxReg(certs[0], certs[1], ca_certs=certs[2], dev=premise.company_id.l10n_si_tax_reg_dev)
                data = premise.with_context(closure=True)._get_export_for_registry()
                if not s.register_business_premise(data):
                    raise exceptions.Warning(_('Registry server did not return expected response.'))

                premise.state = 'cancel'
        finally:
            t.rmtree()

        return True

    def action_draft(self):
        for premise in self:
            premise.state = 'draft'
            premise.delete_workflow()
            premise.create_workflow()

        return True

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'done':
            return 'l10n_si_tax_registry.mt_premise_registered'
        elif 'state' in init_values and self.state == 'cancel':
            return 'l10n_si_tax_registry.mt_premise_closed'
        return super(L10nSiTaxRegPremise, self)._track_subtype(init_values)

    def _get_export_for_registry(self):
        self.ensure_one()
        res = {
            'TaxNumber': int(self.company_id.vat.lstrip('SI')),
            'BusinessPremiseID': self.name,
            'BPIdentifier': {},
            'ValidityDate': self.date,
            'SoftwareSupplier': [{}],
        }

        if self.type == 'real_estate':
            addr = re.match('(.{1,100}) ([0-9]{1,10})(.{0,10})', self.street).groups()
            res['BPIdentifier']['RealEstateBP'] = {
                'PropertyID': {
                    'CadastralNumber': self.number_cadastral,
                    'BuildingNumber': self.number_building,
                    'BuildingSectionNumber': self.number_section_building,
                },
                'Address': {
                    'Street': addr[0],
                    'HouseNumber': addr[1],
                    'Community': self.street2,
                    'City': self.city,
                    'PostalCode': self.zip,
                },
            }
            if addr[2]:
                res['BPIdentifier']['RealEstateBP']['Address']['HouseNumberAdditional'] = addr[2]
        elif self.type == 'movable':
            res['BPIdentifier']['PremiseType'] = self.type_movable.upper()

        if self.env.context.get('closure') != None:
            if self.env.context.get('closure', False):
                res['ClosingTag'] = 'Z'
        elif self.state == 'cancel':
            res['ClosingTag'] = 'Z'

        if self.partner_id.country_id.code.upper().encode('UTF-8') == 'SI':
            res['SoftwareSupplier'][0]['TaxNumber'] = int(self.partner_id.vat.lstrip('SI'))
        else:
            res['SoftwareSupplier'][0]['NameForeign'] = self.partner_id.name + ', ' + \
                self.partner_id.street + ', ' + self.partner_id.zip + ' ' + self.partner_id.city + \
                ', ' + self.partner_id.country_id.name

        if self.comment:
            res['SpecialNotes'] = self.comment

        return res

class L10nSiTaxRegPremiseLine(models.Model):
    _name = 'l10n_si_tax_reg.premise.line'
    _description = 'Business Premise Line'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Electronic device with this name already exists!'),
        ('ir_sequence_id_uniq', 'UNIQUE(ir_sequence_id)', 'This invoice numbering sequence has already been set on another device!'),
    ]

    name = fields.Char(string='Name', length=20, required=True)
    l10n_si_tax_reg_premise_id = fields.Many2one('l10n_si_tax_reg.premise', string='Business Premise', required=True, ondelete='restrict')
    ir_sequence_id = fields.Many2one('ir.sequence', string='Invoice Numbering Sequence', ondelete='set null',
        help='If invoice numbering method is set per electronic device, set the numbering sequence for this device here.')
    ir_sequence_actual_id = fields.Many2one('ir.sequence', string='Actual Invoice Numbering Sequence', compute='_compute_ir_sequence_actual_id')
    number_next_actual = fields.Integer(string='Next Number', compute='_compute_number_next_actual')
    ir_sequence_type = fields.Selection([
            ('c', 'Premise Level'),
            ('b', 'Individual Device'),
            ], string='Invoice Number Assignment Method', compute='_compute_ir_sequence_type')

    description = fields.Text(string='Device Description', translate=True)
    invoice_registered = fields.Boolean(string='Auto-register Finished Invoices', default=True,
        help='Check this box to automatically register invoices of this device.')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('ir_sequence_id', 'l10n_si_tax_reg_premise_id.ir_sequence_id')
    def _compute_ir_sequence_actual_id(self):
        for line in self:
            if line.ir_sequence_id:
                line.ir_sequence_actual_id = line.ir_sequence_id
            else:
                line.ir_sequence_actual_id = line.l10n_si_tax_reg_premise_id.ir_sequence_id

    @api.depends('ir_sequence_id', 'l10n_si_tax_reg_premise_id.ir_sequence_id')
    def _compute_number_next_actual(self):
        for line in self:
            line.number_next_actual = line.ir_sequence_actual_id.number_next_actual

    @api.depends('ir_sequence_id')
    def _compute_ir_sequence_type(self):
        for line in self:
            if line.ir_sequence_id:
                line.ir_sequence_type = 'b'
            else:
                line.ir_sequence_type = 'c'

    @api.constrains('name')
    def _check_name(self):
        for line in self:
            if not re.match('^[0-9a-zA-Z]{1,20}$', line.name):
                raise exceptions.ValidationError(INVALID_FORMAT_MSG % ('name'))

    @api.constrains('ir_sequence_id', 'l10n_si_tax_reg_premise_id')
    def _check_ir_sequence_id(self):
        for line in self:
            if not line.ir_sequence_id and not line.l10n_si_tax_reg_premise_id.ir_sequence_id:
                raise exceptions.ValidationError(_('Either electronic device or its business premise must have invoice numbering sequence set.'))

            if not line.ir_sequence_id:
                continue
            if self.env['l10n_si_tax_reg.premise'].search_count([('ir_sequence_id.id', '=', line.ir_sequence_id.id)]) > 0:
                raise exceptions.ValidationError(_('This sequence already set on one of the business premises.'))

    @api.model
    def create(self, vals):
        business_premise = self.env['l10n_si_tax_reg.premise'].browse(vals['l10n_si_tax_reg_premise_id'])
        if not business_premise.ir_sequence_id and ('ir_sequence_id' not in vals or not vals['ir_sequence_id']):
            vals['ir_sequence_id'] = self.sudo()._create_sequence(vals).id

        return super(L10nSiTaxRegPremiseLine, self).create(vals)

    @api.model
    @api.returns('ir.sequence')
    def _create_sequence(self, data):
        vals = {
            'name': data['name'],
            'code': self.env.ref('l10n_si_tax_registry.ir_sequence_l10n_si_tax_reg').code,
             # 'implementation': 'no_gap',
        }
        if 'l10n_si_tax_reg_premise_id' in data:
            business_premise = self.env['l10n_si_tax_reg.premise'].browse(data['l10n_si_tax_reg_premise_id'])
            vals['name'] = business_premise.name + '-' + vals['name']
            vals['company_id'] = business_premise.company_id.id

        return self.env['ir.sequence'].create(vals)

    def _next(self):
        self.ensure_one()
        return self.ir_sequence_actual_id.next_by_id()
