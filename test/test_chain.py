# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from test.load_external import BlockChain, Block, getkey, coinbase, send, recid, InvalidBlockException
from test.load_external import *
import unittest
import random
import threading


Block.__challenge__ = 2

class TestChain(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK THAT CHAIN CONSTRUCTION
    AND LINKING BLOCKS WORKS AS INTENDED, A NEW BLOCK'S PREV
    HASH CANNOT BE DIFFERENT TO THE LAST BLOCK'S HASH

    AT THE CURRENT TIME, CHAIN BRANCHING IS NOT SUPPORTED,
    MAYBE ADD IT LATER, OR RESOLVE IT IN DB STORAGE
    """

    def makeblock(self, pk, last_hash, last_index):
        return Block(coinbase(pk), last_hash, last_index)

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)
    
    def makechain(self, pk):
        genesis = self.makeblock(pk, '0', 0)
        genesis.calculate_hash()
        return BlockChain([genesis])

    def testMakeValidChainFromLegitBlocksAndValidate(self):
        totalblocks = 6
        sk, pk = getkey()
        chain = self.makechain(pk)
        # make (totalblocks - 1) new blocks, chain already has genesis block
        for _ in range(totalblocks - 1):
            block = self.makeblock(pk, chain.get_last_hash(), chain.get_last_index())
            for _ in range(5):
                t = self.maketransaction(sk, pk, recid())
                block.add(t)
            block.calculate_hash()
            chain.add(block)
        self.assertEqual(chain.validate(), True)
        self.assertEqual(len(chain), totalblocks)

    def testMakeInvalidChainFromCorruptedBlocksIgnoreAndContinue(self):
        totalblocks = 6
        # add invalid block
        invalidblocksindexes = [4]
        sk, pk = getkey()
        chain = self.makechain(pk)

        # make (totalblocks - 1) new blocks, chain already has genesis block
        for _ in range(1, totalblocks):
            block = self.makeblock(pk, chain.get_last_hash(), chain.get_last_index())
            transactions = [self.maketransaction(sk, pk, recid()) for i in range(5)]
            block.add(transactions)
            if _ not in invalidblocksindexes:
                block.calculate_hash()
                chain.add(block)
            else:
                with self.assertRaises(InvalidBlockException) as context:
                    chain.add(block)
                    exception = 'invalid block: {}'.format(block.hash)
                    self.assertTrue(exception == str(context.exception))
        self.assertEqual(chain.validate(), True)    
        self.assertEqual(len(chain), totalblocks - len(invalidblocksindexes))


    def testMakeInvalidChainFromCorruptedBlocksAndNotContinue(self):
        totalblocks = 6
        # add invalid block
        invalidblocksindexes = [3]
        totaladdedblocks = min(invalidblocksindexes)
        sk, pk = getkey()
        chain = self.makechain(pk)

        # make (totalblocks - 1) new blocks, chain already has genesis block
        lasthash = chain.get_last_hash()
        lastindex = chain.get_last_index()
        blocks = []
        for _ in range(1, totalblocks):
            block = self.makeblock(pk, lasthash, lastindex)
            transactions = [self.maketransaction(sk, pk, recid()) for i in range(5)]
            block.add(transactions)
            if _ not in invalidblocksindexes:
                block.calculate_hash()
            blocks.append(block)
            lasthash = block.hash
            lastindex = block.index

        for index, block in enumerate(blocks, 1):
            if index in invalidblocksindexes:
                self.assertRaises(InvalidBlockException, chain.add, [block])
            else: chain.add(block)

        self.assertEqual(chain.validate(), True)    
        self.assertEqual(len(chain), totaladdedblocks)

if __name__ == '__main__':
    unittest.main()

