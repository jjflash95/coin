
import time
import hashlib
import secrets
import string

from encryption.keys.keys import ByteEncoding
from encryption.transaction import Coinbase, Transaction, TransactionArray
from encryption.utils.exceptions import *
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.timestamped import TimeStamped
from encryption.utils.truncate import truncate
import json


class Meanwhile:
    def __init__(self):
        self.value = ''.join([secrets.choice(string.digits) for i in range(10)])
    
    def __str__(self):
        return self.value
    
    @staticmethod
    def calculate_challenge(nodes):
        return 5


class Block(TimeStamped, Jsonifyable):
    __limit__, __challenge__ = 30, 5

    def __init__(self, coinbase, previous_hash = '0', last_index=0, hash=None, meanwhile=None, timestamp=None):
        super().__init__()
        
        if timestamp: self.timestamp = truncate(timestamp)
    
        self.index = last_index + 1
        self.hash, self.meanwhile = hash, meanwhile
        self.previous_hash = previous_hash
        self.coinbase = coinbase
        self.transactions = TransactionArray()
    
    @property
    def challenge(self):
        return self.__challenge__

    @challenge.setter
    def challenge(self, value):
        minimum = 5
        maximum = 62
        if value < minimum:
            value = minimum
        if value > maximum:
            value = maximum
        self.__challenge__ = value

    @staticmethod
    def from_json(data):
        if type(data) == str:
            data = json.loads(data)

        cbase = Coinbase.from_json(data.get('coinbase'))
        block = Block(
            coinbase=cbase,
            previous_hash=data.get('previous_hash'),
            last_index=data.get('index') - 1,
            hash=data.get('hash'),
            meanwhile=data.get('meanwhile'),
            timestamp=data.get('timestamp'))
        
        transactions = [Transaction.from_json(t) for t in data.get('transactions') if t]
        [block.add(t) for t in transactions]

        return block

    def add(self, transactions):
        if not type(transactions) == list:
            transactions = [transactions]
        
        for transaction in transactions:
            if not transaction.validate():
                raise InvalidTransactionException()

            if not self.can_add_transaction():
                raise FullBlockException()

            self._add(transaction)
    
        self.transactions.sort()
        return self   


    def _add(self, transaction: Transaction):
        if self.already_has(transaction):       
            return

        self.transactions.append(transaction)

    def transaction_ids(self):
        return self.transactions.ids()


    def already_has(self, transaction):
        tids = self.transaction_ids()

        return len(tids) != len(set(tids)) or transaction.get_id() in tids
 

    def can_add_transaction(self):
        return len(self.transactions) < self.__limit__


    def calculate_hash(self):
        challenge = '0'*self.__challenge__
        block_data = self.get_block_data()
        start = time.time()
        count = 1
        hash, meanwhile = self.hash_data(block_data)
        while not hash.startswith(challenge):
            hash, meanwhile = self.hash_data(block_data)
            count += 1

        # print('HASH CALCULATED IN {} TRIES! TOOK {} SECONDS'.format(count, time.time() - start))

        self.hash, self.meanwhile = hash, meanwhile        
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
            'timestamp': self.timestamp,
            'meanwhile': str(self.meanwhile)
        }

    def __eq__(self, other):
        if self.hash != other.hash:
            return False
        if self.previous_hash != other.previous_hash:
            return False
        if self.index != other.index:
            return False
        if self.coinbase != other.coinbase:
            return False
        if self.transactions != other.transactions:
            return False


        return True
