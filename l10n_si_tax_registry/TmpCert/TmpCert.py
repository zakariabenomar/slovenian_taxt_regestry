# -*- coding: utf-8 -*-

from base64 import b64decode
import os
import shutil
import tempfile

class TmpCert(object):

    _tmp_dir = None

    def __init__(self, suffix='', prefix='tmp', dir=None):
        self._tmp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def mkstemp(self, suffix='', prefix='tmp', dir=None, text=False):
        dir = self._tmp_dir if dir is None else dir + self._tmp_dir
        return tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)

    def rmtree(self, ignore_errors=False, onerror=None):
        return shutil.rmtree(self._tmp_dir, ignore_errors=ignore_errors, onerror=onerror)

    def record_open_write(self, rec):
        res = [None, None, None]

        if rec.l10n_si_tax_reg_key:
            f = self.mkstemp()
            res[0] = f[1]
            os.write(f[0], b64decode(rec.l10n_si_tax_reg_key))
            os.close(f[0])

        if rec.l10n_si_tax_reg_cert:
            f = self.mkstemp()
            res[1] = f[1]
            os.write(f[0], b64decode(rec.l10n_si_tax_reg_cert))
            os.close(f[0])

        if rec.l10n_si_tax_reg_ca:
            f = self.mkstemp()
            res[2] = f[1]
            os.write(f[0], b64decode(rec.l10n_si_tax_reg_ca))
            os.close(f[0])

        return (res[0], res[1], res[2])
