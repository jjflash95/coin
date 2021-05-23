# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from load_external import Block, getkey, coinbase, send, recid
from load_external import *
import unittest
import random


class TestBlocks(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK THAT BLOCK CONSTRUCTION
    AND VALIDATION IS OK, AND INVALIDATING ITSELF WHEN A NEW
    TRANSACTION IS ADDED AFTER THE HASH HAS BEEN CALCULATED
    (dificculty of 2 zeros for testing)
    """
    def makeblock(self, pk, last_hash, last_index):
        return Block(coinbase(pk), last_hash, last_index)

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)

    def testMakeValidBlockFromValidTransactions(self):
        totaltransactions = 6
        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        for _ in range(totaltransactions):
            t = self.maketransaction(sk, pk, recid())
            block.add(t)
        challenge = 2
        block.calculate_hash(challenge)
        self.assertEqual(block.validate(), True)
        self.assertEqual(len(block.transactions), totaltransactions)

    def testAddMultipleTransactionsAtOnce(self):
        totaltransactions = 6
        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        transactions = []
        for _ in range(totaltransactions):
            t = self.maketransaction(sk, pk, recid())
            transactions.append(t)
        block.add(transactions)
        challenge = 2
        block.calculate_hash(challenge)
        self.assertEqual(block.validate(), True)
        self.assertEqual(len(block.transactions), totaltransactions)

    def testAddTransactionToHashedBlock(self):
        totaltransactions = 6
        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        for _ in range(totaltransactions):
            t = self.maketransaction(sk, pk, recid())
            block.add(t)
        challenge = 2
        block.calculate_hash(challenge)
        self.assertEqual(block.validate(), True)
        self.assertEqual(len(block.transactions), totaltransactions)

        # add new transaction and validate with last hash
        block.add(self.maketransaction(sk, pk, recid()))
        self.assertEqual(block.validate(), False)
        self.assertEqual(len(block.transactions), totaltransactions + 1)


if __name__ == '__main__':
    unittest.main()

