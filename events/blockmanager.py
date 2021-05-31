from encryption.block import Block, Meanwhile
from encryption.generate import block
from encryption.transaction import Transaction

from events.events import Event
from events.listener import EventListener


class BlockManager(EventListener):
    def __init__(self, public, currentblock, storage):
        super(BlockManager, self).__init__()
        self.public = public
        self.block = currentblock
        self.register(Event.NEWTRANSACTION, self.handle_new_transaction)
        self.register(Event.NEWBLOCK, self.handle_new_block)
        self.register(Event.NEWCHAIN, self.handle_new_chain)
        self.register(Event.PEERCOUNT, self.handle_new_peercount)


    def handle_new_transaction(self, transaction):
        if not type(transaction) == Transaction:
            transaction = Transaction.from_json(transaction)

        self.block.add(transaction)
    
    def handle_new_block(self, block):
        if not type(block) == Block:
            block = Block.from_json(block)
        
        self.block = block(self.public, block.hash, block.index)

    def handle_new_peercount(self, peernum):
        self.block.challenge = Meanwhile.calculate_challenge(peernum)
    
    def handle_new_chain(self, chain):
        self.storage.addchain(chain)
