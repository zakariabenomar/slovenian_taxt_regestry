# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Slovenian Tax Registry',
    'version': '9.0.0.1.0',
    'category': 'Localization/Reporting',
    'summary': 'Reports invoices to Slovenian financial administration.',
    'description': """
Slovenian Tax Registration Reporting
====================================

A standard-compliant new FURS tax registration legislation module. For more
information on the new law, please visit the `official FURS fiscal verification
page <http://www.fu.gov.si/en/supervision/podrocja/fiscal_verification_of_invoices_and_pre_numbered_receipt_book/>`_.

So far the reporting module covers:
-----------------------------------
    * Installing and an authenticated connection to the FURS registry data servers
    * Placement and assignment of premises where you conduct your business and and on devices you conducted them on
    * Grouping of taxes based on the FURS tax categorization demands
    * Compatibility with multi-currency and exchange rates
    * Seamless integration of reporting along side your regular invoicing and refunding workflow
    * Foundation for integrating reporting into other models and modules
    * Modification and including all necessary data into your printed reports (code identifiers, custom barcodes, special dates, etc.)
    * A setup wizard to help you get going with your first reporting environment

Future upgrades that will include:
----------------------------------
    * More and better barcode printing support
    * Invoice importing, e.g. pre-numbered invoice book

""",
    'author': 'Editor d.o.o.',
    'maintainer': ['Mitja Uršič', 'Jernej Žorž', 'Hrvoje Margić'],
    'website': 'http://www.editor.si/',
    'depends': [
        'account', 'base'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_message_subtype_data.xml',
        #'l10n_si_tax_reg_premise_workflow.xml',
        'security/ir.model.access.csv',
        'security/l10n_si_tax_registry_security.xml',
        'views/account_config_settings_views.xml',
        'views/account_invoice_views.xml',
        'views/account_tax_views.xml',
        'views/l10n_si_tax_reg_premise_views.xml',
        'views/report_invoice.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'wizard/l10n_si_tax_reg_vat_views.xml',
        'wizard/account_invoice_refund_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
