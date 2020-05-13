# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2016 Editor d.o.o. (<http://editor.si/>).
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

from odoo import api, models

class ReportPointOfSaleReportInvoice(models.AbstractModel):
    _name = 'report.point_of_sale.report_invoice'
    _inherit = ['report.point_of_sale.report_invoice', 'l10n_si_tax_reg.report']

    def render_html(self, data=None):
        for inv in self.env['pos.order'].browse([x.id for x in self]).filtered(lambda r: r.invoice_id and r.invoice_id.l10n_si_tax_reg_premise_line_id).mapped(lambda r: r.invoice_id):
            inv.l10n_si_tax_reg_num_copy += 1

        return super(ReportPointOfSaleReportInvoice, self).render_html(data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
