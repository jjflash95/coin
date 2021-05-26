# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from hashlib import new
import os
import threading

from encryption.block import Block
from encryption.generate import coinbase
from encryption.keys.keys import PublicKey
from events.blockmanager import BlockManager
from events.emitter import Emitter
from localstorage import LocalStorage
from p2p.peer import Peer
from utils import getlastblock

from dotenv import load_dotenv; load_dotenv()


class Client:
    def __init__(self, storage):
        self.storage = storage
 
    def buildp2p(self):
        self.transactionpool = []
        p2p = Peer(os.getenv('MAXPEERS'),
            os.getenv('SERVERPORT'),
            os.getenv('GUID'),
            storage=self.storage)
        p2p.pool = self.transactionpool
        p2p.storage = self.storage
        peers = os.getenv('BUILDFROM').split(' ')
        peers = [p.split(':') for p in peers if p]
        for (host, port) in peers:
            p2p.buildpeers(host, int(port))
        
        self.p2p = p2p

    def listen(self):
        thread = threading.Thread(target=self.p2p.main)
        thread.start()
        return thread
    
    def haschain(self):
        return self.storage.haschain()

    def buildchains(self):
        thread = threading.Thread(target=self.p2p.buildchain)
        thread.start()
        return thread

if __name__ == '__main__':
    public = PublicKey(os.getenv('KEYS_PATH'))
    storage = LocalStorage()
    client = Client(storage)
    client.buildp2p()
    client.listen()
    client.p2p.output = None
    while not client.haschain():
        t = client.buildchains()
        t.join()
    
    chain = storage.getchain(buildcascade=True)
    lastblock = getlastblock(storage)
    print(lastblock)
    print(lastblock)
    print(lastblock)
    print(lastblock)
    newblock = Block(
        coinbase=coinbase(public),
        previous_hash=lastblock.get('bhash'),
        last_index=lastblock.get('bindex'))
    
    manager = BlockManager(public, newblock)
    emitter = Emitter()
    client.p2p.emitter = emitter

    while True:
        newblock.calculate_hash(4)
        storage.addblock(newblock)
        client.p2p.propagate_block(newblock)

