from encryption.block import Block
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.exceptions import *


class BlockChain(Jsonifyable):
    def __init__(self, chain=None):
        self.load(chain)

    def load(self, chain):
        self.chain = []

        if not len(self.chain):
            genesis = chain[0]
            if not genesis.validate():
                raise InvalidBlockException('Invalid genesis block')
            self.chain.append(genesis)

        for block in chain[1:]:
            self.add(block)

        return self

    def remove_block(self):
        self.chain = self.chain[:-1]

    def add(self, blocks: Block):
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
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            for id in current_block.transaction_ids():
                if id in seen_ids:
                    print('detected invalid block: {} with ID: {}'.format(
                        current_block.hash, id))
                    return False
                seen_ids.add(id)
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_last_hash(self):
        return self.chain[-1].hash
    
    def get_last_index(self):
        return self.chain[-1].index

    def to_dict(self):
        return [block.to_dict() for block in self.chain]

    def get_blocks(self):
        for block in self.chain:
            yield block

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.chain)