# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import exceptions

from odoo.http import Controller, route, request

from .. import barcode

class L10nSiTaxRegistryController(Controller):

    @route('/l10n_si_tax_registry/barcode', type='http', auth='user')
    def report_barcode(self, type, value, width=None, height=None, humanreadable=0, lines=1):
        # TODO: Add "PDF417" support.
        # TODO: Support for multiple barcode lines for all codes.
        try:
            bs = barcode.createBarcodeImageInMemory(type, value, width=width and int(width) or None, height=height and int(height) or None, human_readable=bool(humanreadable), lines=lines and int(lines) or 1)
        except (ValueError, AttributeError) as e:
            raise exceptions.HTTPException(description='Cannot convert into barcode.')

        return request.make_response(bs, headers=[('Content-Type', 'image/png')])
