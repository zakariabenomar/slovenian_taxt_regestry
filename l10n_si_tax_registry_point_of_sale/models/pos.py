# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015 Editor d.o.o. (<http://editor.si/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

from odoo.addons.l10n_si_tax_registry import barcode

INVALID_VALUE_MSG = _('Missing or invalid value for "%s"!')

class POSConfig(models.Model):
    _name = 'pos.config'
    _inherit = 'pos.config'

    l10n_si_tax_reg_premise_line_id = fields.Many2one('l10n_si_tax_reg.premise.line', 'Electronic Device', ondelete='set null')
    l10n_si_tax_reg_code_type = fields.Selection([
        ('qr', 'QR'),
        ('code128', 'Code128'),
    ], string='Printed Code Type')
    l10n_si_tax_reg_code_width = fields.Integer(string='Code Width')
    l10n_si_tax_reg_code_height = fields.Integer(string='Code Height')
    l10n_si_tax_reg_code_human_readable = fields.Boolean(string='Human Readable Code',
        help='Should the value used to create the code be displayed also in regular text format.')
    l10n_si_tax_reg_code_num_lines = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ], string='Number of Lines', help='If code image is horizontally too long, it can be split into several lines.')

    @api.constrains('l10n_si_tax_reg_code_type', 'l10n_si_tax_reg_code_width',
        'l10n_si_tax_reg_code_height', 'l10n_si_tax_reg_code_num_lines')
    def _check_l10n_si_tax_reg_code_type(self):
        if not self.l10n_si_tax_reg_code_type:
            return

        if not self.l10n_si_tax_reg_code_width or self.l10n_si_tax_reg_code_width < 1:
            raise exceptions.ValidationError(INVALID_VALUE_MSG % (_('Code Width'),))
        if not self.l10n_si_tax_reg_code_height or self.l10n_si_tax_reg_code_height < 1:
            raise exceptions.ValidationError(INVALID_VALUE_MSG % (_('Code Height'),))

        if self.l10n_si_tax_reg_code_type == 'code128' and not self.l10n_si_tax_reg_code_num_lines:
            raise exceptions.ValidationError(INVALID_VALUE_MSG % (_('Number of Lines'),))


class POSOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'l10n_si_tax_reg.interface']

    _l10n_si_tax_reg_issue_datetime = 'date_order'
    _l10n_si_tax_reg_customer_tax = 'partner_id'
    _l10n_si_tax_reg_value_invoice = 'amount_total'
    _l10n_si_tax_reg_payment_invoice = 'amount_paid'
    _l10n_si_tax_reg_behalf_invoice = 'company_id'
    _l10n_si_tax_reg_taxes = 'lines'
    _l10n_si_tax_reg_issuer_invoice = 'user_id'
    _l10n_si_tax_reg_msg_invoice = 'note'

    _l10n_si_tax_reg_refund_negate = False

    _l10n_si_tax_reg_paid_state_value = ['paid', 'done', 'invoiced']

    @api.model
    def _default_l10n_si_tax_reg_premise_line_id(self):
        session_ids = self._default_session()
        if session_ids:
            session_record = self.env['pos.session'].browse(session_ids)
            return session_record.config_id.l10n_si_tax_reg_premise_line_id and session_record.config_id.l10n_si_tax_reg_premise_line_id[0]

    l10n_si_tax_reg_premise_line_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]}, default=_default_l10n_si_tax_reg_premise_line_id)

    def action_paid(self):
        res = super(POSOrder, self).action_paid()
        self._l10n_si_tax_reg_execute_auto_paid()
        return res

    def refund(self):
        if not self.l10n_si_tax_reg_premise and not self.l10n_si_tax_reg_device and not self.l10n_si_tax_reg_number:
            return super(POSOrder, self).refund()

        self.ensure_one()
        # TODO: Find a way to make this work with multiple orders again.
        res = super(POSOrder, self).refund()
        self.browse(res['res_id']).write({
            'l10n_si_tax_reg_premise_ref': self.l10n_si_tax_reg_premise or False,
            'l10n_si_tax_reg_device_ref': self.l10n_si_tax_reg_device or False,
            'l10n_si_tax_reg_number_ref': self.l10n_si_tax_reg_number or False,
            'l10n_si_tax_reg_date_invoice_ref': self[self._l10n_si_tax_reg_issue_datetime] or False,
        })

        return res

    def action_invoice(self):
        res = super(POSOrder, self).action_invoice()
        for order in self:
            if not order.invoice_id or not order.l10n_si_tax_reg_premise_line_id:
                continue

            order.invoice_id.write({
                'l10n_si_tax_reg_premise_line_id': order.l10n_si_tax_reg_premise_line_id.id,
                'l10n_si_tax_reg_source_model': self._name,
                'l10n_si_tax_reg_source_records': order.id,
            })

        return res

    @api.model
    def _order_fields(self, ui_order):
        res = super(POSOrder, self)._order_fields(ui_order)
        res['l10n_si_tax_reg_num_copy'] = 1
        return res

    def l10n_si_tax_reg_export_for_printing(self, columns=None):
        self.ensure_one()
        res = {}
        if not columns:
            columns = [self._l10n_si_tax_reg_issue_datetime, self._l10n_si_tax_reg_issuer_invoice,
                   'l10n_si_tax_reg_eor', 'l10n_si_tax_reg_zoi', 'l10n_si_tax_reg_barcode',
                   'l10n_si_tax_reg_barcode_base64', 'l10n_si_tax_reg_num_copy']

        if self._l10n_si_tax_reg_issue_datetime in columns:
            res[self._l10n_si_tax_reg_issue_datetime] = self._get_export_for_l10n_si_tax_reg_issue_datetime()
            res[self._l10n_si_tax_reg_issue_datetime] = res[self._l10n_si_tax_reg_issue_datetime] and fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(res[self._l10n_si_tax_reg_issue_datetime]))) or ''
        if self._l10n_si_tax_reg_issuer_invoice in columns:
            res[self._l10n_si_tax_reg_issuer_invoice] = self._get_export_for_l10n_si_tax_reg_issuer_invoice_value()[0]

        for f in ['l10n_si_tax_reg_eor', 'l10n_si_tax_reg_zoi', 'l10n_si_tax_reg_num_copy']:
            if f in columns:
                res[f] = self[f]

        if 'l10n_si_tax_reg_barcode' in columns:
            res['l10n_si_tax_reg_barcode'] = self.get_report_for_l10n_si_tax_reg_barcode()

        if 'l10n_si_tax_reg_barcode_base64' in columns:
            value = res['l10n_si_tax_reg_barcode'] or self.get_report_for_l10n_si_tax_reg_barcode()
            res['l10n_si_tax_reg_barcode_base64'] = base64.b64encode(barcode.createBarcodeImageInMemory(
                self.env.context.get('l10n_si_tax_reg_barcode_name', 'QR'), value,
                width=self.env.context.get('l10n_si_tax_reg_barcode_width', None),
                height=self.env.context.get('l10n_si_tax_reg_barcode_height', None),
                human_readable=self.env.context.get('l10n_si_tax_reg_barcode_human_readable', False),
                lines=self.env.context.get('l10n_si_tax_reg_barcode_lines', barcode.LINES_MIN)))

        return res

class POSOrderLine(models.Model):
    _name = 'pos.order.line'
    _inherit = ['pos.order.line', 'l10n_si_tax_reg.interface.line']

    # FIXME: Tax values are not copied into the order, so if you re-send the
    # order while the taxes have changed in the product, you could face
    # discrepancies in tax amount.
    _l10n_si_tax_reg_account_tax = 'product_id.taxes_id'
    _l10n_si_tax_reg_qty = 'qty'
    _l10n_si_tax_reg_amount = 'price_unit'
    _l10n_si_tax_reg_customer = 'order_id.partner_id'
    _l10n_si_tax_reg_product = 'product_id'

    _l10n_si_tax_reg_discount_percent = 'discount'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
