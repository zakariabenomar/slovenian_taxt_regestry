# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, SUPERUSER_ID

class AccountConfigSettings(models.TransientModel):
    #_name = 'account.config.settings'
    _inherit = 'res.config.settings'

    default_l10n_si_tax_reg_premise_line_id = fields.Many2one('l10n_si_tax_reg.premise.line', string='Default Electronic Device', default_model="account.move",
        domain="[('l10n_si_tax_reg_premise_id.company_id', '=', company_id)]")
    default_l10n_si_tax_reg_force_sent = fields.Boolean(string='Allow issue of invoices without receiving the EOR.', default_model="l10n_si_tax_reg.interface")
    default_l10n_si_tax_reg_partner_id = fields.Many2one('res.partner', string='Your Tax Registry Software Maintainer', default_model="l10n_si_tax_reg.installer.premise")
    module_l10n_si_tax_registry_point_of_sale = fields.Boolean('Point of sale registry management',
        help='This allows point of sale users to register the invoice once its '
             'paid inside the terminal without having to create an actual account invoice first.\n'
             '-This installs the module l10n_si_tax_registry_point_of_sale.')

    def onchange_company_id(self):
        values = super(AccountConfigSettings, self).onchange_company_id()

        if self.company_id:
            IrValues = self.env['ir.values']
            premise_line_id = IrValues.get_default('l10n_si_tax_reg.interface', 'l10n_si_tax_reg_premise_line_id', company_id=self.company_id.id)
            force_sent = IrValues.get_default('l10n_si_tax_reg.interface', 'l10n_si_tax_reg_force_sent', company_id=self.company_id.id)
            partner_id = IrValues.get_default('l10n_si_tax_reg.premise', 'partner_id', company_id=self.company_id.id)
            self.default_l10n_si_tax_reg_premise_line_id = isinstance(premise_line_id, list) and premise_line_id[0] or premise_line_id
            self.default_l10n_si_tax_reg_force_sent = isinstance(force_sent, bool) and force_sent or False
            self.default_l10n_si_tax_reg_partner_id = isinstance(partner_id, list) and partner_id[0] or partner_id

        return values

    def set_default_l10n_si_tax_reg_premise_line(self):
        if self.env.uid != SUPERUSER_ID and not self.env.user.has_group('base.group_erp_manager'):
            raise exceptions.AccessError(_('Only administrators can change the settings'))

        self.env['ir.values'].sudo().set_default('l10n_si_tax_reg.interface', 'l10n_si_tax_reg_premise_line_id',
            self.default_l10n_si_tax_reg_premise_line_id and self.default_l10n_si_tax_reg_premise_line_id.id or False, company_id=self.company_id.id)
        self.env['ir.values'].sudo().set_default('l10n_si_tax_reg.interface', 'l10n_si_tax_reg_force_sent',
            self.default_l10n_si_tax_reg_force_sent or False, company_id=self.company_id.id)
        self.env['ir.values'].sudo().set_default('l10n_si_tax_reg.premise', 'partner_id',
            self.default_l10n_si_tax_reg_partner_id and self.default_l10n_si_tax_reg_partner_id.id or False, company_id=self.company_id.id)
