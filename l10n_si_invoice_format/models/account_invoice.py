# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError, Warning

import logging
_logger=logging.getLogger(__name__)


class AccountInvoice(models.Model):
	_inherit = 'account.move'

	date_invoice = fields.Date(string='Debt Start Date',
		help='Date when debt relationship between customer and issuer started.')	
	date_invoice_creation = fields.Date('Invoice Date', readonly=True,
		states={'draft': [('readonly', False)]}, index=True, default=fields.Date.context_today,
		help='Date when invoice was created.')	
	date_invoice_received = fields.Date('Date Recieved', readonly=True, 
		states={'draft':[('readonly',False)]},
		help="Date when supplier invoice was recieved.")  

		
	warning_invoice_number = fields.Char(readonly=True)
	invisible_warning_invoice_number = fields.Boolean(readonly=True, default=True)
	warning_invoice_dates = fields.Char(readonly=True)
	invisible_warning_invoice_dates = fields.Boolean(readonly=True, default=True)
	
	
	@api.onchange('date_invoice', 'date_invoice_creation')  
	def _validate_date_invoice(self):		
		#Warning: Invoice date must be within 8 days of the Bill date
		if self.type == 'out_invoice':
			if self.date_invoice and self.date_invoice_creation:
				date_format = '%Y-%m-%d'
				date_invoice_creation = datetime.strptime(self.date_invoice_creation, date_format)
				date_invoice = datetime.strptime(self.date_invoice, date_format)
				daysDiff = int((date_invoice-date_invoice_creation).days)	
				if (daysDiff<0 or daysDiff>8):					
					self.invisible_warning_invoice_dates=False
					self.warning_invoice_dates='Invoice date must be within 8 days of the Bill date.'
				else:
					self.invisible_warning_invoice_dates=True
					self.warning_invoice_dates=''
		
		#Warning: Customer invoices exist with Bill date later than self.date_invoice
		if (self.type=='out_invoice'):
			domain = [
				'&',
				('type','=', self.type),
				('state', '!=', 'cancel'),
				('state', '!=', 'draft'),
				('date_invoice', '>', self.date_invoice)			
			]
			date_invoice_later=self.env['account.move'].search_count(domain)

			if (date_invoice_later > 0):
				self.invisible_warning_invoice_number=False
				self.warning_invoice_number = 'You have ' + str(date_invoice_later) + ' invoices with Bill date later than ' + str(self.date_invoice) +'.'
			else:
				self.invisible_warning_invoice_number=True
				self.warning_invoice_number=''
		
	"""
	@api.multi
	def invoice_validate(self):
		self.invisible_warning_invoice_number=True
		self.warning_invoice_number=''
		self.invisible_warning_invoice_dates=True
		self.warning_invoice_dates=''

		
		return super(AccountInvoice, self).invoice_validate()
	"""
			
			
			
			
			
			
			
			
			
			
		