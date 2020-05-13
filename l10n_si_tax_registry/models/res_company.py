# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

from .. SITaxReg.SITaxReg import SITaxReg
from .. TmpCert.TmpCert import TmpCert

class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    l10n_si_tax_reg_key = fields.Binary(string='Private Key', copy=False)
    l10n_si_tax_reg_cert = fields.Binary(string='Public Certificate', copy=False)
    l10n_si_tax_reg_ca = fields.Binary(string='Certification Authority',
        help='When provided, the connection will verify the server authenticity against the input certificate.')
    l10n_si_tax_reg_passphrase = fields.Char(string='Key Passphrase', size=64, copy=False,
        help='If the private key is in encrypted format, the system will use the provided passhrase to decrypt it (not supported at the moment).')
    l10n_si_tax_reg_dev = fields.Boolean(string='Development', help='Are we using development environment.')

    def action_test_l10n_si_tax_reg_conn(self):
        t = TmpCert()
        try:
            for company in self:
                if not company.l10n_si_tax_reg_key or not company.l10n_si_tax_reg_cert:
                    raise exceptions.Warning(_('Missing certificates.'))
                certs = t.record_open_write(company)
                s = SITaxReg(certs[0], certs[1], ca_certs=certs[2], dev=company.l10n_si_tax_reg_dev)
                if not s.echo():
                    raise exceptions.Warning(_('Echo request failed.'))
                # TODO: Request with a signature command.
        finally:
            t.rmtree()

        return True
