# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from reportlab.graphics.shapes import Drawing

from . import QR, Code128

VALUE_LEN = 60
LINES_MIN = 1
LINES_MAX = 6
LINES_FOUR = '4'
CODES = {'QR': QR.QR, 'Code128': Code128.Code128}

def createBarcodeImageInMemory(code_name, value, width=None, height=None, human_readable=False, lines=LINES_MIN):
    if len(value) != VALUE_LEN:
        raise ValueError('Illegal value for value')
    if lines < LINES_MIN or lines > LINES_MAX:
        raise ValueError('Illegal number of lines')

    bc_col = []
    if lines > LINES_MIN:
        i = 1
        lin = lines == int(LINES_FOUR) and LINES_FOUR or ''
        size = VALUE_LEN / lines
        while i < lines:
            x = LINES_FOUR + lin + str(i) + value[:size]
            value = value[size:]
            bc_col.append(CODES[code_name](value=x, human_readable=human_readable))
            i += 1
        value = LINES_FOUR + lin + str(i) + value

    bc = CODES[code_name](value=value, human_readable=human_readable)
    bc_col.append(bc)

    x1, y1, x2, y2 = bc.getBounds()
    w = float(x2 - x1)
    h = float(y2 - y1)
    orig_h = h
    sx = width not in ('auto', None)
    sy = height not in ('auto', None)
    if sx or sy:
        sx = sx and width / w or 1.0
        sy = sy and height / h or 1.0

        w *= sx
        h *= sy
    else:
        sx = sy = 1

    d = Drawing(width=w, height=lines * h, transform=[sx, 0, 0, sy, -sx * x1, -sy * y1])
    bc_col.reverse()
    for i, b in enumerate(bc_col):
        # XXX: Not sure if this is the right way to set the position. It also
        # doesn't work for QR or any future supported codes for that matter.
        b.y = ((i + 1) * orig_h) - orig_h
        d.add(b, '_bc' + str(i))
    return d.asString('png')
