# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Slovenian - Customer Invoice Format',
    'version': '9.0.0.1.0',
    'category': 'Localization',
    'summary': 'Slovenian customer invoice view customization',
    'description': """
Modified Formating of Customer Invoice Form and Report
======================================================

According to the Slovenian legislation, an invoice must report the date of the
day the service has been completed and location where the invoice has been
issued. This module will replace the label of the current date field to reflect
this legislations rule while also creating a new date field to act as a usual
invoice creation date. These new dates will be printed on the invoice reports
along with the company location to satisfy the place of invoice issue
requirement.
""",
    'author': 'Editor d.o.o.',
    'maintainer': 'Igor Zornik <igor.zornik@editor.si>',
    'website': 'http://www.editor.si/',
    'depends': ['account'],
    'data': [
        'views/account_invoice_views.xml',
        'views/report_account_invoice.xml',
    ],
    'qweb': [],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
