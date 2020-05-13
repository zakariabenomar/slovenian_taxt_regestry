# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from reportlab.graphics.barcode import common
from reportlab.graphics.barcode import widgets
from reportlab.graphics.barcode.code128 import Code128 as c128
from reportlab.lib import attrmap

class Code128(widgets._BarcodeWidget, c128):
    _attrMap = attrmap.AttrMap(BASE=widgets.BarcodeI2of5, UNWANTED=('bearers', 'checksum', 'ratio', 'checksum', 'stop'))
    _BCC = c128

    def __init__(self, value='Hello World', human_readable=False):
        # TODO: Set values to match size requirements.
        widgets._BarcodeWidget.__init__(self, _value=value, humanReadable=human_readable)
