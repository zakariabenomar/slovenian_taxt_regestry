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

{
    'name': 'Point of Sale Slovenian Tax Registry',
    'version': '0.1',
    'license': 'AGPL-3',
    'category': 'Localization/Reporting',
    'summary': 'Reports point of sale order to Slovenian financial administration.',
    'description': """
This module adds source invoice support for point of sale module.
""",
    'author': 'Editor d.o.o.',
    'website': 'http://www.editor.si/',
    'depends': [
        'point_of_sale',
        'l10n_si_tax_registry',
        'base',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_views.xml',
        'views/report_order.xml',
        'views/report_invoice.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/l10n_si_tax_registry_point_of_sale.xml'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
