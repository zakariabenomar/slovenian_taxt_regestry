# -*- coding: utf-8 -*-


"""Slovenian tax invoice registration and other commands required by the
system.
"""

import base64
#import Cookie
from http import cookies
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import Crypto.Signature.PKCS1_v1_5 as PKCS
import datetime
from datetime import datetime as dt
#from httplib import HTTPResponse
from http.client import HTTPResponse
#from httplib import OK
from http.client import OK
from logging import debug
#import md5
import hashlib
from OpenSSL import crypto
from re import sub
import json
import socket
import ssl
from uuid import uuid4
from . import exceptions
# from __init__ import __version__
from ..SITaxReg.TmpSock import TmpSock
import logging
_log = logging.getLogger(__name__)


class SITaxReg(object):
    """Slovenian Tax Registry client object."""

    DEBUG_OFF = 0
    DEBUG_SERVER = 1
    DEBUG_CLIENT = 2
    DEBUG_OUTPUT_PRINT = 'print'
    DEBUG_OUTPUT_LOGGER = 'logger'

    SI_TAX_REG_DATE_FORMAT = '%Y-%m-%d'
    SI_TAX_REG_DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    _CRLF = "\r\n"
    _ALGO = 'RS256'

    _keyfile = ''
    _certfile = ''
    _ca_cert = None
    _cert_reqs = ssl.CERT_NONE
    _jws_header = ''
    _key = None
    _crypto_private_key = None
    _debug_output = DEBUG_OUTPUT_PRINT
    _debug = DEBUG_OFF

    _scheme = 'https'
    _host = 'blagajne.fu.gov.si'
    _port = 9003
    _query_string = '/v1/'

    _user_agent = 'Editor d.o.o. SI Tax Registry Python Library/%s'
    _cookies = None

    _message_id = ''
    _request_datetime = None
    _zoi = ''

    def __init__(self, keyfile, certfile, ca_certs=None, key=None, dev=False):
        """Return a new class instance with specified certificates."""
        self._keyfile = keyfile
        self._certfile = certfile
        self._ca_certs = ca_certs
        self._key = key

        # When verifier certificates are provided, we require certificate
        # authentication.
        if self._ca_certs:
            self._cert_reqs = ssl.CERT_REQUIRED

        # self._user_agent = self._user_agent % (__version__)

        if dev:
            self._host = 'blagajne-test.fu.gov.si'
            self._port = 9002

    def set_debug_output(self, output):
        """Set debug output destionation."""
        self._debug_output = output

    def set_debug(self, level):
        """Set debug level."""
        self._debug = level

    def get_message_id(self):
        """Get message ID of last sent message if any."""
        return self._message_id

    def get_request_datetime(self):
        """Get last message request time if any."""
        return self._request_datetime

    def get_zoi(self):
        """Get last used issuer mark in a request if any."""
        return self._zoi

    def echo(self):
        """Send echo request and verify echo server response."""
        res = self.send('cash_registers/echo', {'EchoRequest': 'furs'},
                        sign=False)
        return 'EchoResponse' in res and res['EchoResponse'] == 'furs'

    def register_business_premise(self, data):
        """Register a business premise."""
        self.send('cash_registers/invoices/register', {
            'BusinessPremiseRequest': {'BusinessPremise': data},
        })
        return True

    def issue_electronic_invoice(self, data):
        """Send invoice request for invoices made with an electronic device."""
        res = self.send('cash_registers/invoices', {
            'InvoiceRequest': {'Invoice': self._populate_invoice_data(data)},
        })
        return '' if 'UniqueInvoiceID' not in res else res['UniqueInvoiceID']

    def issue_batch_electronic_invoice(self, data):
        """Send a list of invoices request for invoices made with an electronic
        device.
        """
        data_tmp = []
        for i, d in enumerate(data):
            data_tmp.append({
                'RecordNumber': i + 1,
                'Invoice': self._populate_invoice_data(d),
            })

        res = self.send('cash_registers_batch/invoices', {
            'InvoiceListRequest': {'InvoiceList': {'RecordInfo': data_tmp}},
        })
        data_tmp = []
        if 'RecordReply' not in res:
            return []
        # TODO: Check the response list against the request list.
        return [(r['ProtectedID'],
                r['UniqueInvoiceID']) for r in res['RecordReply']]

    def issue_prenumbered_invoice(self, data):
        """Send invoice request for invoices made with a pre-numbered invoice
        book.
        """
        if 'IssueDate' in data and \
                isinstance(data['IssueDate'], datetime.date):
            data['IssueDate'] = \
                data['IssueDate'].strftime(self.SI_TAX_REG_DATE_FORMAT)
        if 'ReferenceSalesBook' in data and \
                isinstance(data['ReferenceSalesBook'], list) and \
                len(data['ReferenceSalesBook']) > 0 and \
                'ReferenceSalesBookIssueDate' in \
                data['ReferenceSalesBook'][0] and \
                isinstance(
                    data['ReferenceSalesBook'][0]
                        ['ReferenceSalesBookIssueDate'],
                    datetime.date
                ):
            data['ReferenceSalesBook'][0]['ReferenceSalesBookIssueDate'] = \
                data['ReferenceSalesBook'][0]['ReferenceSalesBookIssueDate'] \
                .strftime(self.SI_TAX_REG_DATE_FORMAT)
        if 'ReferenceInvoice' in data and \
                isinstance(data['ReferenceInvoice'], list) and \
                len(data['ReferenceInvoice']) > 0 and \
                'ReferenceInvoiceIssueDateTime' in \
                data['ReferenceInvoice'][0] and \
                isinstance(
                    data['ReferenceInvoice'][0]
                        ['ReferenceInvoiceIssueDateTime'],
                    datetime.datetime
                ):
            data['ReferenceInvoice'][0]['ReferenceInvoiceIssueDateTime'] = \
                data['ReferenceInvoice'][0]['ReferenceInvoiceIssueDateTime'] \
                .strftime(self.SI_TAX_REG_DT_FORMAT)

        res = self.send('cash_registers/invoices', {
            'InvoiceRequest': {'SalesBookInvoice': data},
        })
        return '' if 'UniqueInvoiceID' not in res else res['UniqueInvoiceID']

    def send(self, endpoint, data, sign=True):
        """Send request data to registry server."""
        self._message_id = ''
        self._request_datetime = None
        self._zoi = ''

        if isinstance(data, str):
            data = json.loads(data)

        if 'InvoiceRequest' in data and \
                'Invoice' in data['InvoiceRequest'] and \
                'ProtectedID' in data['InvoiceRequest']['Invoice']:
            self._zoi = data['InvoiceRequest']['Invoice']['ProtectedID']
        elif 'InvoiceListRequest' in data and \
                'InvoiceList' in data['InvoiceListRequest'] and \
                'RecordInfo' in data['InvoiceListRequest']['InvoiceList']:
            str_tmp = len(data['InvoiceListRequest']['InvoiceList']
                          ['RecordInfo'])
            if str_tmp > 0:
                str_tmp = (data['InvoiceListRequest']['InvoiceList']
                           ['RecordInfo'][str_tmp - 1])
                if 'Invoice' in str_tmp and \
                        'ProtectedID' in str_tmp['Invoice']:
                    self._zoi = str_tmp['Invoice']['ProtectedID']

        if sign:
            data = self._inject_header(data)
            str_tmp = data.iterkeys().next()
            self._message_id = data[str_tmp]['Header']['MessageID']
            self._request_datetime = dt.strptime(
                data[str_tmp]['Header']['DateTime'],
                self.SI_TAX_REG_DT_FORMAT
            )
            data = self._sign(data)

        conn = ssl.wrap_socket(socket.socket(), keyfile=self._keyfile,
                               certfile=self._certfile,
                               cert_reqs=self._cert_reqs,
                               ca_certs=self._ca_certs)
        conn.connect((self._host, self._port))

        if not isinstance(data, str):
            data = json.dumps(data)
        str_tmp = [
            'POST %s%s HTTP/1.1' % (self._query_string, endpoint),
            'Host: %s:%d' % (self._host, self._port),
            'User-Agent: ' + (self._user_agent),
            'Content-Type: application/json; charset=UTF-8',
            'Connection: close',
            'Content-Length: ' + str(len(data))
        ]
        if self._cookies:
            str_tmp.append(
                'Cookie: ' + '; '.join([
                    x + '=' + self._cookies[x].value for x in self._cookies]
                )
            )

        data = self._CRLF.join(str_tmp) + self._CRLF + self._CRLF + data
        self._e_debug("\n" + '---SENDING---' + "\n" + data + "\n" +
                      '---END---' + "\n", self.DEBUG_CLIENT)

        try:
            data_write =data
            conn.write(data_write.encode())
        except Exception as e:
            conn.close()
            raise e

        data = ''
        str_tmp = True
        while str_tmp != '':
            str_tmp = conn.read(4096).decode()
            data += str_tmp
        conn.close()
        str_tmp = None

        self._e_debug("\n" + '---GOT---' + "\n" + data + "\n" +
                      '---END---' + "\n", self.DEBUG_SERVER)
        data = self._parse_http_response(data)

        # TODO: Improve cookie management.
        c = data.getheader('Set-Cookie') or data.getheader('Cookie')
        self._cookies = cookies.SimpleCookie(c) if c else None

        if data.status != OK:
            raise exceptions.SITaxServerError(data.read(), data.status)

        data = data.read()
        print('result:',data)
        data = json.loads(data)
        _log.info('\n*--------\n'
                  '*RECEIVE: %s\n'
                  '*-----------\n', data)
        if sign:
            data = self._parse_signed_response(data)
            # Take only the payload.
            data = data[1]
            # Get sub-content.
            data = data.itervalues().next()
            # Remove header.
            del (data['Header'])
            # Any potencial errors should be stored here. If found, raise an
            # exception.
            if 'Error' in data:
                raise exceptions.SITaxRegistryError(
                    data['Error']['ErrorMessage'],
                    data['Error']['ErrorCode']
                )

        return data

    def get_session_cookie(self):
        """Get session cookie object."""
        return self._cookies

    def set_session_cookie(self, cookie):
        """Set session cookie object."""
        self._cookies = cookie

    def _inject_header(self, data, uid=None, dtm=None):
        """Insert message identification in first and only child of dict."""
        if not uid:
            uid = str(uuid4())
        if not dtm:
            dtm = dt.utcnow()
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            raise TypeError('Data inappropriate to perform signature on')
        if len(data) != 1:
            raise ValueError('Data inappropriate to perform signature on')
        h = data.iterkeys().next()
        if not isinstance(data[h], dict):
            raise TypeError('Data inappropriate to perform signature on')
        data[h]['Header'] = {
            'MessageID': uid,
            'DateTime': dtm.strftime(self.SI_TAX_REG_DT_FORMAT),
        }
        return data

    def _sign(self, data):
        """Sign the request message."""
        h = self._get_jws_header() + '.' + self._jws_base64_encode(
            json.dumps(data))
        return {'token': h + '.' + self._signature(h)}

    def _signature(self, data):
        """Create a signature out of a certificate header and already encoded
        and joined message payload.
        """
        self._check_and_load_private_key()

        h = SHA256.new(data.encode('UTF-8'))
        return self._jws_base64_encode(
            PKCS.new(self._crypto_private_key).sign(h))

    def _parse_http_response(self, response_str):
        """Parse response string into an HTTP object."""
        sock = TmpSock(response_str)
        res = HTTPResponse(sock)
        res.begin()
        print('res', res.getheaders())
        return res

    def _parse_signed_response(self, data):
        """Parse and fix encoded response from the tax registry server."""
        res = []
        data = data['token'].split('.')
        signature = data.pop()
        # Parse JWS header and payload.
        for d in data:
            res.append(json.loads(self._jws_base64_decode(d)))
        # TODO: Parse signature.
        res.append(signature)
        return res

    def _get_jws_header(self):
        """Parse if necessary and get public certificate JWS header."""
        if self._jws_header == '':
            # If header hasn't been made yet, construct it and store in buffer
            # for possible later access.
            # TODO: This is the only place where we need the OpenSSL module.
            # See if we can somehow read the data without it so we can remove
            # the dependency.
            b = open(self._certfile, 'r').read()
            x = crypto.load_certificate(crypto.FILETYPE_PEM, b)

            jws_header = {
                'alg': self._ALGO,
                'subject_name': ','.join(map(lambda x: x[0] + '=' + x[1],
                                         x.get_subject().get_components())),
                'issuer_name': ','.join(map(lambda x: x[0] + '=' + x[1],
                                        x.get_issuer().get_components())),
                'serial': x.get_serial_number(),
            }

            self._jws_header = self._jws_base64_encode(json.dumps(jws_header))

        return self._jws_header

    def _jws_base64_encode(self, s):
        """Encode string into a JWS compliant base64 format."""
        return base64.urlsafe_b64encode(s).replace(b'=', b'')

    def _jws_base64_decode(self, s):
        """Decode string from a JWS base64 format."""
        s += b'=' * (4 - (len(s) % 4))
        return base64.urlsafe_b64decode(s.encode('UTF-8'))

    def _calculate_protective_mark(self, tax_number, date, invoice_number,
                                   premise, device, amount):
        """Generate "ZOI" signature."""
        self._check_and_load_private_key()
        sig = str(tax_number) + date + invoice_number + premise + device \
            + str(amount)
        sig = SHA256.new(sig.encode('UTF-8')).digest()
        sig = self._crypto_private_key.sign(sig, '')[0]
        return hashlib.md5.new(str(sig)).hexdigest()

    def _populate_invoice_data(self, data):
        """Add missing and correct existing data in invoice dict."""
        if 'IssueDateTime' in data and \
                isinstance(data['IssueDateTime'], datetime.datetime):
            data['IssueDateTime'] = \
                data['IssueDateTime'].strftime(self.SI_TAX_REG_DT_FORMAT)
        if 'ReferenceInvoice' in data and \
                isinstance(data['ReferenceInvoice'], list) and \
                len(data['ReferenceInvoice']) > 0 and \
                'ReferenceInvoiceIssueDateTime' in \
                data['ReferenceInvoice'][0] and \
                isinstance(
                    data['ReferenceInvoice'][0]
                        ['ReferenceInvoiceIssueDateTime'],
                    datetime.datetime
                ):
            data['ReferenceInvoice'][0]['ReferenceInvoiceIssueDateTime'] = \
                data['ReferenceInvoice'][0]['ReferenceInvoiceIssueDateTime'] \
                .strftime(self.SI_TAX_REG_DT_FORMAT)
        if 'ReferenceSalesBook' in data and \
                isinstance(data['ReferenceSalesBook'], list) and \
                len(data['ReferenceSalesBook']) > 0 and \
                'ReferenceSalesBookIssueDate' in \
                data['ReferenceSalesBook'][0] and \
                isinstance(
                    data['ReferenceSalesBook'][0]
                        ['ReferenceSalesBookIssueDate'],
                    datetime.date
                ):
            data['ReferenceSalesBook'][0]['ReferenceSalesBookIssueDate'] = \
                data['ReferenceSalesBook'][0]['ReferenceSalesBookIssueDate'] \
                .strftime(self.SI_TAX_REG_DATE_FORMAT)

        if 'ProtectedID' not in data:
            data['ProtectedID'] = self._calculate_protective_mark(
                data['TaxNumber'], data['IssueDateTime'],
                data['InvoiceIdentifier']['InvoiceNumber'],
                data['InvoiceIdentifier']['BusinessPremiseID'],
                data['InvoiceIdentifier']['ElectronicDeviceID'],
                data['InvoiceAmount']
            )
        _log.info('\n*-----------\n'
                  '*SEND: %s\n'
                  '*-------------\n', data)
        return data

    def _check_and_load_private_key(self):
        """Load the private key content into class property."""
        if not self._crypto_private_key:
            h = open(self._keyfile, 'r').read()
            self._crypto_private_key = RSA.importKey(h, passphrase=self._key)

    def _e_debug(self, msg, level):
        """Output debug message to user-selected method."""
        if level > self._debug:
            return

        if self._debug_output == 'logger':
            debug(msg)
        else:
            msg = sub('/(\r\n|\r|\n)/ms', "\n", msg)
            print( dt.now().strftime('%Y-%m-%d %H:%M:%S') + "\t" \
                + msg.strip() + "\n")
