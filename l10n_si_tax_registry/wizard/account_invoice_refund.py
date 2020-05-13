# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_log = logging.getLogger(__name__)


class AccountInvoiceRefund(models.TransientModel):
	_inherit = "account.move.reversal"

	@api.model
	def _get_tax_reg(self):
		print('test')
		invoice_id = self.env['account.move'].browse(self._context.get('active_id', False))
		print('test 2')
		if invoice_id.l10n_si_tax_reg_premise_line_id:
			print('test3')
			return True
		return False

	l10n_si_tax_reg_check = fields.Boolean(default=_get_tax_reg)
