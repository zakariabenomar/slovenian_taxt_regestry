# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from reportlab.graphics.barcode import qrencoder as qr
from reportlab.graphics.shapes import Group, Rect
from reportlab.graphics.widgetbase import Widget
from reportlab.lib import colors
from reportlab.lib.utils import asNative
from reportlab.lib.units import mm

class QR(Widget):
    value = ''

    def __init__(self, value='Hello World', human_readable=False):
        # TODO: Add support to set "y" bound.
        self.value = str(value) if isinstance(value, int) else asNative(value)

    def draw(self):
        g = Group()
        g_add = g.add
        bar_width, bar_height, x, y = 32 * mm, 32 * mm, 0, 0
        g_add(Rect(x, y, bar_width, bar_height, fillColor=None, strokeColor=None, strokeWidth=0))

        bar_fill_color, bar_stroke_width, bar_stroke_color, bar_border = colors.black, 0, None, 4

        qrbc = qr.QRCode(2, qr.QRErrorCorrectLevel.M)
        qrbc.addData(self.value)
        qrbc.make()

        module_count = qrbc.getModuleCount()
        box_size = min(bar_width, bar_height) / (module_count + bar_border * 2)
        offset_x = (bar_width - min(bar_width, bar_height)) / 2
        offset_y = (min(bar_width, bar_height) - bar_height) / 2

        for r in xrange(module_count):
            for c in xrange(module_count):
                if (qrbc.isDark(r, c)):
                    x = (c + bar_border) * box_size
                    y = (r + bar_border + 1) * box_size
                    q_rect = Rect(offset_x + x, offset_y + bar_height - y, box_size, box_size, fillColor=bar_fill_color, strokeWidth=bar_stroke_width, strokeColor=bar_stroke_color)
                    g_add(q_rect)

        return g
