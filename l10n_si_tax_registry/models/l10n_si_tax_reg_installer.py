# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models, SUPERUSER_ID
from odoo.tools.translate import _

class L10nSiTaxRegInstaller(models.TransientModel):
    _name = 'l10n_si_tax_reg.installer'
    _inherit = 'res.config.installer'

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.move'))
    private_key = fields.Binary(string='Private Key', required=True,
        help='You should get this file when requesting your registration with the tax institute.')
    public_cert = fields.Binary(string='Public Certificate', required=True,
        help='You should get this file when requesting your registration with the tax institute.')
    authority_cert = fields.Binary(string='Certification Authority',
        help='Upload this certificate if you wish that all further connections to the registry are authenticated against this file.')
    dev_mode = fields.Boolean(string='Developers Environment',
        help='Check this if you want all the requests to go to a test server. No data will be written to live environment.')

    def modules_to_install(self):
        res = super(L10nSiTaxRegInstaller, self).modules_to_install()
        if 'dev_mode' in res:
            res.remove('dev_mode')
        return res

    def execute(self):
        if self.env.uid != SUPERUSER_ID and not self.env.user.has_group('base.group_erp_manager'):
            raise exceptions.AccessError(_('Only administrators can change the settings'))

        self._install_registry()
        if self.env.context.get('test_connection', False):
            self.company_id.action_test_l10n_si_tax_reg_conn()

        ref = self.env.ref('l10n_si_tax_registry.l10n_si_tax_reg_installer_premise_view_form')
        res = self.next()
        if isinstance(res, dict) and 'res_model' in res and \
                res['res_model'] == ref.model and \
                'view_id' in res and res['view_id'][0] == ref.id:
            res['context'].update(default_company_id=self.company_id.id)

        return res

    def _install_registry(self):
        self.company_id.write({
            'l10n_si_tax_reg_key': self.private_key,
            'l10n_si_tax_reg_cert': self.public_cert,
            'l10n_si_tax_reg_ca': self.authority_cert or False,
            'l10n_si_tax_reg_dev': self.dev_mode or False,
        })

class L10nSiTaxRegInstallerPremise(models.TransientModel):
    _name = 'l10n_si_tax_reg.installer.premise'
    _inherit = 'res.config.installer'

    l10n_si_tax_reg_premise_id = fields.Many2one('l10n_si_tax_reg.premise', string='Business Premise')
    # FIXME: This should default to value set in previous step if gone through work flow.
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.move'))
    name = fields.Char(string='Business Premise ID', size=20,
        help='Enter business premise name if you want to create a new one.')
    res_partner_id = fields.Many2one('res.partner', string='Existing Address',
        help='Select business premise if you want to use an existing address.')
    partner_id = fields.Many2one('res.partner', string='Software Maintainer', required=True)
    ir_sequence_id = fields.Many2one('ir.sequence', string='Invoice Numbering Sequence',
        help='Numbering sequence that will be used when generating paid invoices. If none is provided, one will be created for you.')
    ir_sequence_type = fields.Selection([
                ('c', 'Premise Level'),
                ('b', 'Individual Device'),
                ], string='Invoice Number Assignment Method', required=True, default='c',
        help=" * 'Premise Level' - numbers are assigned centrally at the level of business level.\r"
             " * 'Individual Device' - assign numbers per each device individually.")
    force_sent = fields.Boolean(string='Enable Force Send',
        help='By default skip invoice registration when registration is not possible.')

    type = fields.Selection([
            ('real_estate', 'Real Estate'),
            ('movable', 'Movable'),
            ], string='Premise Type', required=True, default='real_estate')
    type_movable = fields.Selection([
            ('a', 'Mobile'),
            ('b', 'Stationary'),
            ('c', 'Other'),
            ], string='Movable Type',
        help=" * 'Mobile' - movable object such as a vehicle or movable stand.\n"
             " * 'Stationary' - object at a permanent location (e.g. market or news stand).\n"
             " * 'Other' - No other available business premise used for issuing invoices.")

    number_cadastral = fields.Integer(string='Cadastral Number')
    number_building = fields.Integer(string='Building Number')
    number_section_building = fields.Integer(string='Part Number of Building')

    date = fields.Date(string='Valid Date', help='Premise valid start date.')
    street = fields.Char(string='Address', size=120)
    street2 = fields.Char(string='Community', size=100)
    city = fields.Char(string='City', size=40)
    zip = fields.Char(string='ZIP', size=4)

    comment = fields.Text(string='Extra Notes', help='Any special information you would like the tax institution to know?')

    electronic_device_name = fields.Char(string='Electronic Device Name', size=20,
        help='Electronic device used to make invoices. This record will be set as default device when making new invoices.')
    electronic_device_description = fields.Text(string='Electronic Device Description',
        help='Any extra information that should be known about this device (for internal use only).')

    @api.one
    @api.constrains('ir_sequence_type', 'electronic_device_name')
    def _check_electronic_device_name(self):
        if self.ir_sequence_type == 'b' and not self.electronic_device_name:
            raise exceptions.ValidationError('Electronic device must be set up when using device-based numbering.')

    def modules_to_install(self):
        res = super(L10nSiTaxRegInstallerPremise, self).modules_to_install()
        if 'force_sent' in res:
            res.remove('force_sent')
        return res

    def execute(self):
        if self.env.uid != SUPERUSER_ID and not self.env.user.has_group('base.group_erp_manager'):
            raise exceptions.AccessError(_('Only administrators can change the settings'))

        self._install_registry()
        if self.env.context.get('register_premise', False):
            self.l10n_si_tax_reg_premise_id.signal_workflow('l10n_si_tax_reg_premise_done')

        return super(L10nSiTaxRegInstallerPremise, self).execute()

    def _install_registry(self):
        account_config_data = {
            'company_id': self.company_id,
            'default_l10n_si_tax_reg_partner_id': self.partner_id,
        }

        if not self.res_partner_id:
            self.res_partner_id = self._generate_address()

        if not self.ir_sequence_id:
            self.ir_sequence_id = self._generate_sequence()

        vals = {
            'res_partner_id': self.res_partner_id.id,
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'type': self.type,
            'type_movable': self.type_movable,
            'number_cadastral': self.number_cadastral,
            'number_building': self.number_building,
            'number_section_building': self.number_section_building,
        }
        if self.ir_sequence_type == 'c':
            vals['ir_sequence_id'] = self.ir_sequence_id.id
        self.l10n_si_tax_reg_premise_id = self.env['l10n_si_tax_reg.premise'].create(vals)

        if self.force_sent:
            account_config_data['default_l10n_si_tax_reg_force_sent'] = True

        if self.electronic_device_name:
            vals = {
                'name': self.electronic_device_name,
                'l10n_si_tax_reg_premise_id': self.l10n_si_tax_reg_premise_id.id,
                'description': self.electronic_device_description,
            }
            if self.ir_sequence_type == 'b':
                vals['ir_sequence_id'] = self.ir_sequence_id.id
            device = self.env['l10n_si_tax_reg.premise.line'].create(vals)
            account_config_data['default_l10n_si_tax_reg_premise_line_id'] = device

        self.env['account.config.settings'].new(account_config_data).set_default_l10n_si_tax_reg_premise_line()

    @api.returns('res.partner')
    def _generate_address(self):
        vals = {
            'country_id': self.env.ref('base.si').id,
            'customer': False,
        }
        for val in ['name', 'date', 'street', 'street2', 'city', 'zip', 'comment']:
            vals[val] = self[val] or ''
        return self.env['res.partner'].create(vals)

    @api.returns('ir.sequence')
    def _generate_sequence(self, data):
        vals = {
            'name': self.res_partner_id.name,
            'code': self.env.ref('l10n_si_tax_registry.seq_type_l10n_si_tax_reg').code,
            'implementation': 'no_gap',
            'company_id': self.company_id.id,
        }
        if self.electronic_device_name:
            vals['name'] = vals['name'] + '-' + self.electronic_device_name

        return self.env['ir.sequence'].create(vals)

# class L10nSiTaxRegInstallerAccountTax(models.TransientModel):
#     _name = 'l10n_si_tax_reg.installer.account.tax'
#     _inherit = 'res.config.installer'

#     company_id = fields.Many2one('res.company', string='Company', required=True,
#         default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
#     l10n_si_tax_reg_installer_account_tax_line_ids = fields.One2many('l10n_si_tax_reg.installer.account.tax.line',
#         'l10n_si_tax_reg_installer_account_tax_id', string='Account Tax List')

#     @api.one
#     @api.constrains('company_id', 'l10n_si_tax_reg_installer_account_tax_line_ids')
#     def _check_l10n_si_tax_reg_installer_account_tax_line_ids(self):
#         for line in self.l10n_si_tax_reg_installer_account_tax_line_ids:
#             if self.company_id.id != line.company_id.id:
#                 raise exceptions.ValidationError('Selected tax(es) must belong to the same company we are modifying.')

    # FIXME: Remove on check and instead erase tax list on company change.
    # @api.onchange('company_id')
    # def _onchange_company_id(self):

#     @api.multi
#     def execute(self):
#         if self.env.uid != SUPERUSER_ID and not self.env.user.has_group('base.group_erp_manager'):
#             raise exceptions.AccessError(_('Only administrators can change the settings'))

        # self._install_registry()

#         return super(L10nSiTaxRegInstallerAccountTax, self).execute()

# class L10nSiTaxRegInstallerAccountTaxLine(models.TransientModel):
#     _name = 'l10n_si_tax_reg.installer.account.tax.line'
#     _sql_constraints = [
#         ('account_tax_id_uniq', 'UNIQUE(l10n_si_tax_reg_installer_account_tax_id, account_tax_id)', 'Tax can have only one tax registry group!'),
#     ]

#     l10n_si_tax_reg_installer_account_tax_id = fields.Many2one('l10n_si_tax_reg.installer.account.tax.line', ondelete='cascade')
#     account_tax_id = fields.Many2one('account.tax', string='Account Tax', required=True)
#     type = fields.Selection([
#             ('regular', 'Regular'),
#             ('flat', 'Flat-Rate'),
#             ('other', 'Other'),
#             ('exempt', 'Tax Exempt'),
#             ('reverse', 'Reverse Charge Procedure'),
#             ('notax', 'Non-Taxable'),
#             ('special', 'Special'),
#             ], string='Tax Type', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
