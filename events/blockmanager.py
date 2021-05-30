from encryption.block import Block, Meanwhile
from encryption.generate import coinbase
from encryption.transaction import Transaction

from events.events import Event
from events.listener import EventListener


class BlockManager(EventListener):
    def __init__(self, public, currentblock):
        super(BlockManager, self).__init__()
        self.public = public
        self.block = currentblock
        self.register(Event.NEW_TRANSACTION, self.handle_new_transaction)
        self.register(Event.NEW_BLOCK, self.handle_new_block)
        self.register(Event.PEERCOUNT, self.handle_new_peercount)


    def handle_new_transaction(self, transaction):
        if not type(transaction) == Transaction:
            transaction = Transaction.from_json(transaction)

        self.block.add(transaction)
    
    def handle_new_block(self, block):
        if not type(block) == Block:
            block = Block.from_json(block)
        
        self.block = Block(coinbase=coinbase(self.public),
            previous_hash=block.hash,
            last_index=block.index)

    def handle_new_peercount(self, peernum):
        self.block.challenge = Meanwhile.calculate_challenge(peernum)
    