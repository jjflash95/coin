
import hashlib
import secrets
import string

from keys.keys import ByteEncoding
from transaction import Transaction, Reward, TransactionArray
from transaction import CorruptedTransactionException
from utils.jsonifyable import Jsonifyable
from utils.timestamped import TimeStamped



class CorruptedBlockException(Exception):
    pass

class FullBlockException(Exception):
    pass


class ProofOfWork:
    def __init__(self):
        self.value = ''.join([secrets.choice(string.digits) for i in range(10)])
    
    def __str__(self):
        return self.value


class Block(TimeStamped, Jsonifyable):
    limit = 10

    def __init__(self, reward, previous_hash = 0):
        super().__init__()
        self.hash, self.proof_of_work = None, None
        self.previous_hash = previous_hash
        self.transactions = TransactionArray()
        self.reward = reward


    def add(self, transaction: Transaction):
        if not transaction.validate():
            raise CorruptedTransactionException()

        if not self.can_add_transaction():
            raise FullBlockException()

        return self._add(transaction)
        

    def _add(self, transaction: Transaction):
        if self.already_has(transaction):       
            return self

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
        
        bhash, bpow = self.hash_data(block_data)
        while not bhash.startswith(challenge):
            bhash, bpow = self.hash_data(block_data)
            
        self.hash, self.proof_of_work = bhash, bpow
        
        return self


    def hash_data(self, block, bpow = None):
        hashf = lambda h: hashlib.sha256(
            bytes(h, ByteEncoding.ENCODING)).hexdigest()
        
        bpow = bpow and bpow or ProofOfWork() 

        block['pow'] = str(bpow)
        serialized_block = self.jsonify(block)

        return hashf(serialized_block), bpow

    def validate(self):
        return self.hash == self.hash_data(self.get_block_data(), self.proof_of_work)[0]
  

    def get_block_data(self):
        return {
            'previous_hash': self.previous_hash,
            'transactions': self.transactions.to_dict()
        }


    def to_dict(self):
        return {
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'reward': self.reward.to_dict(),
            'transactions': [t.to_dict() for t in self.transactions.all()],
            'timestamp': self.timestamp(),
            'proof_of_work': str(self.proof_of_work)
        }

