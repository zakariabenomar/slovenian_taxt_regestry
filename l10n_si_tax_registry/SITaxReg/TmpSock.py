# -*- encoding: utf-8 -*-

#from StringIO import StringIO
from io import StringIO,BytesIO


class TmpSock():
    """Buffer used by HTTPResponse to parse response string into response
    object.
    """

    def __init__(self, response_str):
        self._file = BytesIO(response_str.encode())

    def makefile(self, *args, **kwargs):
        return self._file
