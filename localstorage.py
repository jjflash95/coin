from storage.storage import Storage
from storage.models.models import BlockModel
from storage.models.models import ChainModel
from encryption.block import Block
from encryption.transaction import Coinbase, Transaction
from encryption.blockchain import BlockChain


class LocalStorage:
    def __init__(self, onmemory=False):
        self.storage = Storage(onmemory=onmemory)

    def addblock(self, block: Block):
        self.storage.addblock(block)
        return self
    
    def addchain(self, chain):
        if type(chain) == str:
            chain = BlockChain.from_json(chain)

        if not chain.validate():
            return

        self.storage.addchain(chain)
        return self

    def addcoinbase(self, blockhash, coinbase: Coinbase):
        self.storage.addcoinbase(blockhash, coinbase)
        return self

    def addtransaction(self, blockhash, transaction: Transaction):
        self.storage.addtransaction(blockhash, transaction)
        return self
    
    def getblock(self, blockhash, buildcascade=False):
        return BlockModel.build(self.storage.getblock(blockhash, buildcascade))

    def getchain(self, buildcascade=True):
        chain = self.storage.getchain(buildcascade)

        if not buildcascade:
            return chain
    
        return ChainModel.build(chain)

    def haschain(self):
        return len(self.storage.getchain(buildcascade=False))

