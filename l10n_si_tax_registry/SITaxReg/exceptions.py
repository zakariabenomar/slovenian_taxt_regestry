# -*- encoding: utf-8 -*-


class SITaxServerError(Exception):
    """Raised when server returns a response with an invalid status code."""

    def __init__(self, message, status):
        super(SITaxServerError, self).__init__('[' + str(status) + '] ' +
                                               message)
        self.status = status


class SITaxRegistryError(Exception):
    """Raised when server software returns an error in response."""

    def __init__(self, message, code):
        super(SITaxRegistryError, self).__init__('[' + code + '] ' + message)
        self.code = code
