# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_log = logging.getLogger(__name__)


class ResCurrency(models.Model):
	_inherit = 'res.currency'

	def compute_at_date(self, from_amount, from_currency, to_currency, at_date, rounded=True):
		if from_currency == to_currency:
			return from_amount
		else:
			from_currency_rates = sorted(self.env['res.currency.rate'].search([('currency_id', '=', from_currency.id), ('name', '<=', at_date)]), key=lambda r: r.name, reverse=True)
			if not from_currency_rates:
				from_currency_rate_at_date = 1.0
			else:
				from_currency_rate_at_date = from_currency_rates[0].rate

			to_currency_rates = sorted(self.env['res.currency.rate'].search([('currency_id', '=', to_currency.id), ('name', '<=', at_date)]), key=lambda r: r.name, reverse=True)
			if not to_currency_rates:
				to_currency_rate_at_date = 1.0
			else:
				to_currency_rate_at_date = to_currency_rates[0].rate
			to_amount = from_amount * to_currency_rate_at_date/from_currency_rate_at_date
			return to_currency.round(to_amount) if rounded else to_amount
