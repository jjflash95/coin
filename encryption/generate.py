from encryption.utils.exceptions import InvalidKeyException
import hashlib

from cryptography.exceptions import InvalidKey

from encryption.keys.keys import ByteEncoding, PrivateKey, PublicKey
from encryption.transaction import Transaction
from encryption.transaction import Coinbase
from encryption.utils.timestamped import TimeStamped


class Send(TimeStamped):
    secret, public = None, None

    def __init__(self, secret: PrivateKey, public: PublicKey, recipient_id, amount):
        super().__init__()
        if not secret or not public:
            raise InvalidKeyException()
    
        self.transaction = self.generate_transaction(secret, public, recipient_id, amount)

    def generate_transaction(self, secret, public, recipient_id, amount):
        tid = self.generate_id(
            str(public),
            recipient_id,
            amount,
            self.timestamp)

        transaction = Transaction(tid, str(public), recipient_id, amount)
        signature = self.get_signature(secret, transaction.get_data())
        transaction.set_signature(signature)
        return transaction

    def generate_id(self, sender_id, recipient_id, amount, timestamp):
        string = '{}{}{}{}'.format(sender_id, recipient_id, amount, timestamp)
        return hashlib.sha256(bytes(string, ByteEncoding.ENCODING)).hexdigest()

    def get_signature(self, secret, encoded_str):
        return secret.sign(encoded_str)

    def get_transaction(self):
        return self.transaction


class BlockCoinbase(Send):
    AMOUNT = 10

    def __init__(self, public: PublicKey):
        super(Send, self).__init__()
        self.id = self.generate_id(
            str(public),
            str(public),
            BlockCoinbase.AMOUNT,
            self.timestamp)

        self.transaction = Coinbase(self.id, str(public), BlockCoinbase.AMOUNT)

    def generate_transaction(self, recipient_id, amount):
        tid = self.generate_id(
            str(self.public),
            recipient_id,
            amount,
            self.timestamp)

        return Coinbase(tid, recipient_id, amount)

    def to_dict(self):
        return {
            'data': self.data
        }

    def to_json(self):
        return self.transaction.to_json()


def send(secret, public, recipient_id, amount):
    return Send(secret, public, recipient_id, amount).get_transaction()

def coinbase(public):
    return BlockCoinbase(public).get_transaction()
