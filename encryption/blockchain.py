from encryption.block import Block
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.exceptions import *


class BlockChain(Jsonifyable):
    def __init__(self, blocks=None):
        self.load(blocks)

    def load(self, blocks):
        self.chain = []

        if not len(self.chain):
            genesis = blocks[0]
            if not genesis.validate():
                raise InvalidBlockException('Invalid genesis block')
            self.chain.append(genesis)

        for block in blocks[1:]:
            self.add(block)

        return self

    def remove_block(self):
        self.chain = self.chain[:-1]

    def add(self, blocks):
        if type(blocks) != list:
            blocks = [blocks]
        
        for block in blocks:
            if not block.validate():
                raise InvalidBlockException('invalid block: {}'.format(block.hash))
            self.chain.append(block)

            while not self.validate() and len(self.chain) > 1:
                self.remove_block()

        return self

    def validate(self):
        seen_ids = set()
        for previndex, currentblock in enumerate(self.chain[1:]):
            previous_block = self.chain[previndex]
            for id in currentblock.transaction_ids():
                if id in seen_ids: return False
                seen_ids.add(id)
            if currentblock.previous_hash != previous_block.hash:
                return False

        return True

    def get_last_hash(self):
        return self.chain[-1].hash
    
    def get_last_index(self):
        return self.chain[-1].index

    def to_dict(self):
        return [block.to_dict() for block in self.chain]

    def getblocks(self):
        for block in self.chain:
            yield block

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.chain)
    
    def __eq__(self, other):
        if len(self.chain) != len(other.chain):
            return False
        
        for i, block in enumerate(self.chain):
            if block != other.chain[i]:
                return False
        
        return True