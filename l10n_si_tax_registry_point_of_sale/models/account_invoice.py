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

from odoo import api, models

class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    def _get_export_for_l10n_si_tax_reg_point_of_sale_report(self):
        self.ensure_one()
        if self.l10n_si_tax_reg_source_model != 'pos.order':
            return None

        return self.env['pos.order'].browse(int(self.l10n_si_tax_reg_source_records.split(',')[0]))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
