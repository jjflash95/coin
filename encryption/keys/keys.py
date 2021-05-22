# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false

import base64
import hashlib
import re
from abc import ABCMeta, abstractmethod

from cryptography.exceptions import InvalidKey, InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


class ByteEncoding:
    ENCODING = 'UTF-8'  

    @staticmethod
    def to_bytes(data):
        if not isinstance(data, bytes):
            data = bytes(data, ByteEncoding.ENCODING)
        return data


class Key(ByteEncoding, metaclass=ABCMeta):
    __key__, __path__ = None, None

    def __init__(self, path=None, key=None):
        if path is None and key is None:
            raise InvalidKey()

        self.set_path(path)
        self.set_key(key)


    def key(self):
        if self.__key__ is None: self.load()
        return self.__key__


    def set_key(self, key):
        if key is not None: self.__key__ = self.serialize(Key.to_bytes(key))
        return self

    def set_path(self, path):
        if path is not None: self.__path__ = path
        return self

    def load(self):
        with open('{}/{}'.format(self.__path__, self.KEY), "rb") as key_file:
            self.__key__ = self.serialize(key_file.read())

    def __eq__(self, other):
        if not isinstance(other, Key):
            return False

        return self.__str__() == other.__str__()


    @staticmethod
    @abstractmethod
    def serialize(data):
        pass


class Signature(ByteEncoding):
    _signature = None

    def __init__(self, signature):
        if Signature.isb64(signature):
            signature = base64.b64decode(signature)
        
        self._signature = self.to_bytes(signature)


    @staticmethod
    def isb64(signature):
        pattern = '^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$'
        pattern = re.compile(pattern)
        return pattern.match(str(signature))

    def signature(self, as_string=False):
        if as_string:
            return base64.b64encode(self._signature).decode(ByteEncoding.ENCODING)
        return self._signature     


    def __str__(self):
        return self.signature(as_string=True)


class PrivateKey(Key):
    KEY = 'private_key.pem'

    @staticmethod
    def serialize(data):       
        return serialization.load_pem_private_key(
                data,
                password=None,
                backend=default_backend()
            )


    @staticmethod
    def from_string(string):
        return PrivateKey(key=string)


    def id(self):
        return hashlib.md5(self.__str__().encode(ByteEncoding.ENCODING)).hexdigest()


    def sign(self, message):
        return Signature(self.key().sign(
                            Key.to_bytes(message),
                            padding=padding.PKCS1v15(),
                            algorithm=hashes.SHA256()))


    def __str__(self):
        return self.key().private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()).decode(ByteEncoding.ENCODING)


class PublicKey(Key):
    KEY = 'public_key.pem'

    @staticmethod
    def serialize(data):
        return serialization.load_pem_public_key(
            data,
            backend=default_backend()
        )


    @staticmethod
    def from_string(string):
        begin = '-----BEGIN PUBLIC KEY-----\n'
        end = '\n-----END PUBLIC KEY-----'

        if not string.startswith(begin):
            string = '{}{}'.format(begin, string)
        
        if not string.endswith(end):
            string = '{}{}'.format(string, end)

        return PublicKey(key=string)


    def _load(self):
        with open('{}/{}'.format(self.__path__, self.KEY), "rb") as key_file:
            return serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )


    def verify(self, data, signature: Signature):
        try:
            self.key().verify(
                signature=signature.signature(),
                data=Key.to_bytes(data),
                padding=padding.PKCS1v15(),
                algorithm=hashes.SHA256()
            )
        except InvalidSignature as e:
            return False
        
        return True


    def id(self):
        return hashlib.md5(self.__str__().encode(ByteEncoding.ENCODING)).hexdigest()


    def __str__(self):
        string = self.key().public_bytes(
            Encoding.PEM,
            PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return re.sub(r'\n?-----(BEGIN|END) PUBLIC KEY-----\n?', '', string)
    
