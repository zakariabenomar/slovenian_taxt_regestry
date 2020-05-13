# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class ReportAccountReportInvoice(models.AbstractModel):
    _name = 'report.account.report_invoice'
    _inherit = 'l10n_si_tax_reg.report'
