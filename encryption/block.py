
import hashlib
import secrets
import string

from encryption.keys.keys import ByteEncoding
from encryption.transaction import Transaction, TransactionArray
from encryption.utils.exceptions import *
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.timestamped import TimeStamped


class Meanwhile:
    def __init__(self):
        self.value = ''.join([secrets.choice(string.digits) for i in range(10)])
    
    def __str__(self):
        return self.value


class Block(TimeStamped, Jsonifyable):
    limit = 10

    def __init__(self, coinbase, previous_hash = '0', last_index=0):
        super().__init__()
        self.index = last_index + 1
        self.hash, self.meanwhile = None, None
        self.previous_hash = previous_hash
        self.transactions = TransactionArray()
        self.coinbase = coinbase


    def add(self, transactions: Transaction):
        if not type(transactions) == list:
            transactions = [transactions]
        
        for transaction in transactions:
            if not transaction.validate():
                raise InvalidTransactionException()

            if not self.can_add_transaction():
                raise FullBlockException()

            self._add(transaction)
        return self   

    def _add(self, transaction: Transaction):
        if self.already_has(transaction):       
            return

        self.transactions.append(transaction)
        self.transactions.sort()


    def transaction_ids(self):
        return self.transactions.ids()


    def already_has(self, transaction):
        tids = self.transaction_ids()

        return len(tids) != len(set(tids)) or transaction.get_id() in tids
 

    def can_add_transaction(self):
        return len(self.transactions) < self.limit


    def calculate_hash(self, challenge: int):
        challenge = '0'*challenge
        block_data = self.get_block_data()
        
        bhash, bmeanwhile = self.hash_data(block_data)
        while not bhash.startswith(challenge):
            bhash, bmeanwhile = self.hash_data(block_data)
            
        self.hash, self.meanwhile = bhash, bmeanwhile
        
        return self


    def hash_data(self, block, bpow = None):
        hashf = lambda h: hashlib.sha256(
            bytes(h, ByteEncoding.ENCODING)).hexdigest()
        
        bpow = bpow and bpow or Meanwhile() 

        block['pow'] = str(bpow)
        serialized_block = self.jsonify(block)

        return hashf(serialized_block), bpow

    def validate(self):
        return self.hash == self.hash_data(self.get_block_data(), self.meanwhile)[0]
  

    def get_block_data(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': self.transactions.to_dict()
        }


    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'coinbase': self.coinbase.to_dict(),
            'transactions': [t.to_dict() for t in self.transactions.all()],
            'timestamp': self.timestamp(),
            'meanwhile': str(self.meanwhile)
        }
