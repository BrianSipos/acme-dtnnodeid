import binascii
import base64
from cryptography.hazmat.primitives import hashes
from jwcrypto import jwk
import logging
import unittest
from scapy_cbor.util import encode_diagnostic

LOGGER = logging.getLogger(__name__)


def b64enc(data):
    ''' Base-64 encode with trailing removal.
    '''
    enc = base64.urlsafe_b64encode(data)
    enc = enc.strip(b'=')
    return enc.decode('latin1')


def hash(data):
    ''' Perform SHA-256 digest
    '''
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize()


class TestExample(unittest.TestCase):

    def test(self):
        print()
        jwk_data = b'hello'
        key_tp = hash(jwk_data)
        key_tp_enc = b64enc(key_tp)

        print('Thumbprint:', encode_diagnostic(key_tp))
        print('Thumbprint b64url:', encode_diagnostic(key_tp_enc))

        part1 = binascii.unhexlify(b'a77c916055382b1c1068742327645d89')
        part1_enc = b64enc(part1)
        print('Token Part-1:', encode_diagnostic(part1))
        print('Token Part-1 b64url:', encode_diagnostic(part1_enc))
        part2 = binascii.unhexlify(b'b4f519358e0e34893a2f112b44512357')
        part2_enc = b64enc(part2)
        print('Token Part-2:', encode_diagnostic(part2))
        print('Token Part-2 b64url:', encode_diagnostic(part2_enc))

        key_auth = part1_enc + part2_enc + '.' + key_tp_enc
        print('Key Auth.:', encode_diagnostic(key_auth))
        key_auth_digest = hash(key_auth.encode('latin1'))
        print('Key Auth. digest:', encode_diagnostic(key_auth_digest, bstr_as='base64url'))
