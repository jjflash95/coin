from encryption.block import Block
from encryption.utils.jsonifyable import Jsonifyable
from encryption.utils.exceptions import *
import json
import os


class BlockChain(Jsonifyable):

    def __init__(self, blocks=[]):
        self.add(blocks)

    @staticmethod
    def from_json(string):
        chain = json.loads(string)
        blocks = [Block.from_json(block) for block in chain]
        return BlockChain(blocks)

    def remove_block(self):
        self.chain = self.chain[:-1]

    def add(self, blocks):
        if not hasattr(self, 'chain'):
            self.chain = []

        if type(blocks) != list:
            blocks = [blocks]
        
        for block in blocks:
            if not block.validate():
                if os.environ.get('DEBUGMODE', False):
                    print('invalid block: {}'.format(block.hash))
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
        if not self.chain:
            return '0'

        return self.chain[-1].hash
    
    def get_last_index(self):
        if not self.chain:
            return 0

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
