import json
from encryption.keys.keys import ByteEncoding, PublicKey, Signature
from encryption.utils.exceptions import *
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.truncate import truncate


class Transaction(Jsonifyable):
    def __init__(self, id, sender_id, recipient_id, amount, signature=None):
        if not sender_id or not recipient_id:
            raise InvalidKeyException()
        if amount < 0:
            raise InvalidAmountException()

        self.signature = signature
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = truncate(amount)

    @staticmethod
    def from_json(data):
        import json
        if type(data) == str:
            data = json.loads(data)
        tid = data.get('id')
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        amount = truncate(data.get('amount'))
        signature = data.get('signature')

        return Transaction(tid, sender_id, recipient_id, amount, Signature(signature))


    def get_id(self):
        return self.id

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'amount': self.amount,
            'signature': str(self.signature)
        }

    def set_signature(self, signature):
        self.signature = signature
        return self

    def get_data(self):
        return self.jsonify({
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'amount': self.amount,
        })

    def sign(self, signature):
        self.set_signature(signature(self.jsonify(self.get_data())))
        return self

    def assertparams(self):
        if self.amount < 0:
            return False
        return True

    def validate(self):
        if not self.assertparams():
            return False

        public = PublicKey.from_string(self.sender_id)
        return public.verify(
            self.get_data(),
            self.signature)
    
    def __eq__(self, other):
        if type(other) != Transaction:
            try:
                other = Transaction.from_json(other)
            except Exception as e:
                return False

        if self.id != other.id:
            return False
        if self.sender_id != other.sender_id:
            return False
        if self.recipient_id != other.recipient_id:
            return False
        if self.amount != other.amount:
            return False

        return True


class Coinbase(Transaction):
    AMOUNT = 10

    def __init__(self, id, recipient_id):
        self.id = id
        self.recipient_id =  recipient_id
        self.amount = truncate(Coinbase.AMOUNT)
    
    @staticmethod
    def from_json(data):
        import json
        if type(data) == str:
            data = json.loads(data)
        
        return Coinbase(data.get('id'), data.get('recipient_id'))


    def to_dict(self):
        return {
            'id': self.id,
            'recipient_id': self.recipient_id,
            'amount': self.amount
        }
    
    def validate(self):
        return self.amount == Coinbase.AMOUNT
    
    def __eq__(self, other):
        if self.id != other.id:
            return False
        if self.recipient_id != other.recipient_id:
            return False
        if self.amount != other.amount:
            return False

        return True


class TransactionArray:
    def __init__(self):
        self.transactions = []

    def append(self, transactions: Transaction):
        if not type(transactions) == list:
            transactions = [transactions]
        for transaction in transactions:
            self.transactions.append(transaction)
        return self.sort()

    def to_dict(self):
        return [t.to_dict() for t in self.transactions]

    def ids(self):
        return [t.get_id() for t in self.transactions]

    def all(self):
        return self.transactions

    def sort(self):
        self.transactions.sort(key=lambda x: x.get_id())
        return self

    def __len__(self):
        return len(self.transactions)

    def __eq__(self, other):
        self.sort()
        other.sort()

        if len(self.transactions) != len(other.transactions):
            return False
    
        for i, transaction in enumerate(self.transactions):
            if transaction != other.transactions[i]:
                return False

        return True
