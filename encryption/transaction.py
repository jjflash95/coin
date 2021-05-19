from utils.jsonifyable import Jsonifyable
from keys.keys import ByteEncoding, PublicKey, Signature



class CorruptedTransactionException(Exception):
    pass


class Transaction(Jsonifyable):
    def __init__(self, id, sender_id, recipient_id, amount, signature=None):
        self.signature = signature
        self.data = {
            'id': id,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'amount': amount
        }


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
        return self.data.get('id')

    def to_dict(self):
        return {
            'data': self.data,
            'signature': str(self.signature)
        }

    def set_signature(self, signature):
        self.signature = signature
        return self

    def get_data(self):
        return self.jsonify(self.data)

    def sign(self, signature):
        self.set_signature(signature(self.jsonify(self.data)))
        return self


    def validate(self):
        public = PublicKey.from_string(self.data.get('sender_id'))
        return public.verify(
            self.jsonify(self.data),
            self.signature)


class Reward(Transaction):
    def __init__(self, id, recipient_id, amount):
        self.data = {
            'id': id,
            'recipient_id': recipient_id,
            'amount': amount
        }
    
    def to_dict(self):
        return {'data': self.data}
    
    def validate(self):
        return self.data.get('amount') == Reward.amount


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
        sortfunc = lambda x: x.get_id()
        self.transactions.sort(key=sortfunc)

    def __len__(self):
        return len(self.transactions)
