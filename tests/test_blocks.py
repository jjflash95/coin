# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from load_external import Block, getkey, coinbase, send, recid
from load_external import *
import os
import unittest
import random


class TestKeys(unittest.TestCase):
    
    def makeblock(self, pk, last_hash, last_index):
        return Block(coinbase(pk), last_hash, last_index)

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)

    def testMakeValidBlockFromValidTransactions(self):
        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        for _ in range(5):
            t = self.maketransaction(sk, pk, recid())
        block.add(t)
        challenge = 2
        block.calculate_hash(challenge)
        self.assertEqual(block.validate(), True)    

    def testAddTransactionToHashedBlock(self):
        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        for _ in range(5):
            t = self.maketransaction(sk, pk, recid())
        block.add(t)
        challenge = 2
        block.calculate_hash(challenge)

        # add new transaction and validate with last hash
        block.add(self.maketransaction(sk, pk, recid()))
        self.assertEqual(block.validate(), False)

 

if __name__ == '__main__':
    unittest.main()