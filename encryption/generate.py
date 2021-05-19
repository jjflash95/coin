import hashlib

from keys.keys import ByteEncoding, PrivateKey, PublicKey, Signature
from transaction import Transaction
from transaction import Reward
from utils.timestamped import TimeStamped


class Send(TimeStamped):
    secret, public = None, None

    def __init__(self, secret: PrivateKey, public: PublicKey, recipient_id, amount):
        super().__init__()
        self.secret = secret
        self.public = public
        self.transaction = self.generate_transaction(recipient_id, amount)

    
    def generate_transaction(self, recipient_id, amount):       
        tid = self.generate_id(
                            str(self.public),
                            recipient_id,
                            amount,
                            self.timestamp())
    
        transaction = Transaction(tid, str(self.public), recipient_id, amount)
        signature = self.get_signature(transaction.get_data())
        transaction.set_signature(signature)
        return transaction


    def generate_id(self, sender_id, recipient_id, amount, timestamp):
        string = '{}{}{}{}'.format(sender_id, recipient_id, amount, timestamp)
        return hashlib.sha256(bytes(string, ByteEncoding.ENCODING)).hexdigest()


    def get_signature(self, encoded_str):
        return self.secret.sign(encoded_str)

    
    def get_transaction(self):
        return self.transaction


class BlockReward(Send):
    AMOUNT = 10

    def __init__(self, public: PublicKey):
        super(Send, self).__init__()
        self.id = self.generate_id(
                                str(public),
                                str(public),
                                BlockReward.AMOUNT,
                                self.timestamp())

        self.transaction = Reward(self.id, str(public), BlockReward.AMOUNT)

    def generate_transaction(self, recipient_id, amount):
        tid = self.generate_id(
                            str(self.public),
                            recipient_id,
                            amount,
                            self.timestamp())
    
        return Reward(tid, recipient_id, amount)


    def to_dict(self):
        return {
            'data': self.data
        }

    def to_json(self):
        return self.transaction.to_json()


def send(secret, public, recipient_id, amount):
    return Send(secret, public, recipient_id, amount).get_transaction()

def reward(public):
    return BlockReward(public).get_transaction()

