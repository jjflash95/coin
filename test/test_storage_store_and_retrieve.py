# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false

from test.load_external import BlockChain, Block, getkey, coinbase, send, recid, Storage, ChainModel
import unittest
import random
import threading


Block.__challenge__ = 2


class TestChainWithStorage(unittest.TestCase):
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
        t = send(sk, pk, recipient_id, amount)
        return t

    def makechain(self, pk):
        genesis = self.makeblock(pk, '0', 0)
        genesis.calculate_hash()
        return BlockChain([genesis])

    def makefullblock(self, sk, pk, recipient_id, last_hash, last_index, length=3):
        block = self.makeblock(pk, last_hash, last_index)
        for i in range(length):
            t = self.maketransaction(sk, pk, recipient_id, random.random())
            t.validate()
            block.add(t)
        block.calculate_hash()
        return block

    def makefullchain(self, sk, pk, recid, length):
        chain = self.makechain(pk)
        for _ in range(1, length):
            chain.add(self.makefullblock(sk, pk, recid, chain.get_last_hash(), chain.get_last_index()))
        return chain

    def testMakeValidChainFromLegitBlocksAndValidate(self):
        """
        BUILDS BLOCKCHAIN VIA API, STORES IT IN MEMORY DB
        RETRIEVES IT FROM MEMDB AND BUILDS AGAIN THE BLOCKCHAIN
        EACH TRANSACTION HAS TO BE SORTED IN ORDER FOR HASHES
        TO BE CORRECT, TRUNCATED AMOUNT TO 6 DECIMALS AND TIMESTAMP
        SO DB DOESN'T ROUND THEM ON STORAGE (HASH CHANGES AND 
        SIGNATURE DOES NOT VALIDATE, NICE BUG TO CATCH =D)
        """
        totalblocks = 3
        sk, pk = getkey()
        storage = Storage(path=False)
        chain = self.makefullchain(sk, pk, recid(), totalblocks)
        storage.addchain(chain)

        hollowblocks = storage.getchain(buildcascade=False)

        self.assertEqual(len(chain), len(hollowblocks))
        for i, block in enumerate(chain.getblocks()):
            self.assertEqual(block.hash, hollowblocks[i].get('bhash'))
        
        b = storage.getchain(buildcascade=True)
        blockchain = ChainModel.build(b)

        self.assertTrue(chain == blockchain)


if __name__  == '__main__':
    unittest.main()

# '000000000000000000076c036ff5119e5a5a74df77abf64203473364509f7732'
# '00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048'