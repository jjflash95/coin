from encryption.utils.jsonifyable import Jsonifyable
from encryption.keys.keys import ByteEncoding, PublicKey, Signature


class Transaction(Jsonifyable):
    def __init__(self, id, sender_id, recipient_id, amount, signature=None):
        self.signature = signature
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount



    @staticmethod
    def from_json(data):
        import json
        data = json.loads(data, encoding=ByteEncoding.ENCODING)
        tid = data.get('data').get('id')
        sender_id = data.get('data').get('sender_id')
        recipient_id = data.get('data').get('recipient_id')
        amount = data.get('data').get('amount')
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


    def validate(self):
        public = PublicKey.from_string(self.sender_id)
        return public.verify(
            self.get_data(),
            self.signature)


class Coinbase(Transaction):
    def __init__(self, id, recipient_id, amount):
        self.id = id
        self.recipient_id =  recipient_id
        self.amount = amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_id': self.recipient_id,
            'amount': self.amount
        }
    
    def validate(self):
        return self.amount == Coinbase.amount


class TransactionArray:
    def __init__(self):
        self.transactions = []

    def append(self, transaction: Transaction):
        self.transactions.append(transaction)
        return self

    def to_dict(self):
        return [t.to_dict() for t in self.transactions]

    def ids(self):
        return [t.get_id() for t in self.transactions]

    def all(self):
        return self.transactions

    def sort(self):
        self.transactions.sort(key=lambda x: x.get_id())

    def __len__(self):
        return len(self.transactions)
