import hashlib

from encryption.keys.keys import ByteEncoding, PrivateKey, PublicKey
from encryption.transaction import Coinbase, Transaction
from encryption.block import Block
from encryption.blockchain import BlockChain
from encryption.utils.exceptions import InvalidKeyException
from encryption.utils.truncate import truncate
import datetime


def __makeid(sender_id, recipient_id, amount):
    timestamp = truncate(datetime.datetime.now().timestamp())
    string = '{}{}{}{}'.format(sender_id, recipient_id, amount, timestamp)
    return hashlib.sha256(bytes(string, ByteEncoding.ENCODING)).hexdigest()

def coinbase(public):
    if not public:
        raise InvalidKeyException()

    cid = __makeid(str(public), str(public), Coinbase.AMOUNT)
    return Coinbase(cid, str(public))


def send(secret, public, recipient_id, amount):
    if not secret or not public:
        raise InvalidKeyException()

    # generate transaction id
    tid = __makeid(str(public), recipient_id, amount)

    # instantiate transaciton with id, send_id, recp_id and amount
    transaction = Transaction(tid, str(public), recipient_id, amount)

    # sign transaction with private key
    signature = secret.sign(transaction.get_data())
    transaction.set_signature(signature)

    return transaction

def block(publickey, last_hash, last_index):
    return Block(coinbase(publickey), last_hash, last_index)

def chain(blocks=[]):
    return BlockChain(blocks)
