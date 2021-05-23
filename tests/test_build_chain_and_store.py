
# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from load_external import BlockChain, Block, getkey, coinbase, send, recid, InvalidBlockException, Storage
from load_external import *
import unittest
import random



class TestChainWithStorage(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK THAT CHAIN CONSTRUCTION
    AND LINKING BLOCKS WORKS AS INTENDED, A NEW BLOCK'S PREV
    HASH CANNOT BE DIFFERENT TO THE LAST BLOCK'S HASH

    AT THE CURRENT TIME, CHAIN BRANCHING IS NOT SUPPORTED,
    MAYBE ADD IT LATER, OR RESOLVE IT IN DB STORAGE
    """

    challenge = 2
    
    def makeblock(self, pk, last_hash, last_index):
        return Block(coinbase(pk), last_hash, last_index)

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)
    
    def makechain(self, pk):
        genesis = self.makeblock(pk, '0', 0)
        genesis.calculate_hash(self.challenge)
        return BlockChain([genesis])

    def makefullblock(self, sk, pk, recipient_id, last_hash, last_index, length=3):
        block = self.makeblock(pk, last_hash, last_index)
        for i in range(length):
            t = self.maketransaction(sk, pk, recipient_id, random.random())
            t.validate()
            block.add(t)
        block.calculate_hash(self.challenge)
        return block

    def makefullchain(self, sk, pk, recid, length):
        chain = self.makechain(pk)
        for _ in range(1, length):
            chain.add(self.makefullblock(sk, pk, recid, chain.get_last_hash(), chain.get_last_index()))
        return chain

    def testMakeValidChainFromLegitBlocksAndValidate(self):
        totalblocks = 2
        sk, pk = getkey()
        storage = Storage(onmemory=True)

        chain = self.makefullchain(sk, pk, recid(), totalblocks)
        storage.addchain(chain)
        print(chain.validate())
        print(chain)
        print(storage.getblocks(True))


if __name__  == '__main__':
    unittest.main()
