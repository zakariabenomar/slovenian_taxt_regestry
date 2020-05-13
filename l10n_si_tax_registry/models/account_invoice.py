# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _
import logging

_log = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'l10n_si_tax_reg.interface']

    _l10n_si_tax_reg_issue_datetime = 'l10n_si_tax_reg_date_invoice'
    _l10n_si_tax_reg_customer_tax = 'partner_id'
    _l10n_si_tax_reg_value_invoice = 'amount_total'
    _l10n_si_tax_reg_behalf_invoice = 'company_id'
    _l10n_si_tax_reg_taxes = 'invoice_line_ids'
    _l10n_si_tax_reg_issuer_invoice = 'user_id'
    _l10n_si_tax_reg_msg_invoice = 'comment'
    _l10n_si_tax_reg_currency = 'currency_id'
    _l10n_si_tax_reg_date_debt = 'date_invoice'

    _l10n_si_tax_reg_paid_state_value = 'open'

    l10n_si_tax_reg_premise_line_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]})
    l10n_si_tax_reg_date_invoice = fields.Datetime(string='Invoice Issued', states={'paid': [('readonly', True)], 'cancel': [('readonly', True)]},
        help='The exact time the invoice has been issued to the recipient. Will set current time if empty upon invoice payment.')

    l10n_si_tax_reg_source_model = fields.Char(readonly=True, states={'draft': [('readonly', False)]})
    l10n_si_tax_reg_source_records = fields.Char(readonly=True, states={'draft': [('readonly', False)]})

    def invoice_validate(self):
        if not self.l10n_si_tax_reg_date_invoice and self.l10n_si_tax_reg_premise_line_id:
            self.l10n_si_tax_reg_date_invoice = fields.Datetime().now()

        if self.type.split('_')[0] != 'out':
            return super(AccountInvoice, self).invoice_validate()

        res = super(AccountInvoice, self).invoice_validate()
        self._l10n_si_tax_reg_execute_auto_paid()
        return res

    # This part is still useful if we want to send to FURS when registering payments. Needs _l10n_si_tax_reg_paid_state_value = 'paid'.
    # @api.multi
    # def confirm_paid(self):
    #     if not self.l10n_si_tax_reg_date_invoice and self.l10n_si_tax_reg_premise_line_id:
    #         self.l10n_si_tax_reg_date_invoice = fields.Datetime().now()
    #
    #     if self.type.split('_')[0] != 'out':
    #         return super(AccountInvoice, self).confirm_paid()
    #
    #     res = super(AccountInvoice, self).confirm_paid()
    #     self._l10n_si_tax_reg_execute_auto_paid()
    #     return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
        if invoice.type != 'out_invoice':
            return values

        for field in ['l10n_si_tax_reg_premise', 'l10n_si_tax_reg_device', 'l10n_si_tax_reg_number']:
            values[field + '_ref'] = invoice[field] or False
        values['l10n_si_tax_reg_date_invoice_ref'] = invoice[self._l10n_si_tax_reg_issue_datetime] or False
        # Refunds of tax registered invoices must have an electronic device set. Since refunds are in draft they can be
        # altered but at least this field won't be left empty
        values['l10n_si_tax_reg_premise_line_id'] = invoice.l10n_si_tax_reg_premise_line_id.id or False

        return values


class AccountInvoiceLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'l10n_si_tax_reg.interface.line']

    date_invoice = fields.Date(related='move_id.invoice_date')

    _l10n_si_tax_reg_account_tax = 'invoice_line_tax_ids'
    _l10n_si_tax_reg_qty = 'quantity'
    _l10n_si_tax_reg_amount = 'price_unit'
    _l10n_si_tax_reg_customer = 'partner_id'
    _l10n_si_tax_reg_product = 'product_id'
    _l10n_si_tax_reg_behalf_invoice = 'company_id'
    _l10n_si_tax_reg_currency = 'currency_id'
    _l10n_si_tax_reg_date_debt = date_invoice

    _l10n_si_tax_reg_discount_percent = 'discount'