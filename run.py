import os
import threading

from client import Client
from encryption.block import Block, Meanwhile
from encryption.generate import coinbase
from encryption.keys.keys import PublicKey
from events.blockmanager import BlockManager
from events.emitter import Emitter
from localstorage import LocalStorage
from p2p.peer import Peer
from utils import getlastblock

from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
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
    newblock = Block(
        coinbase=coinbase(public),
        previous_hash=lastblock.get('bhash'),
        last_index=lastblock.get('bindex'))
    
    manager = BlockManager(public, newblock)
    emitter = Emitter()
    client.p2p.emitter = emitter

    while True:
        newblock.calculate_hash()
        storage.addblock(newblock)
        client.p2p.propagate_block(newblock)
        lastblock = newblock
        newblock = Block(
            coinbase=coinbase(public),
            previous_hash=lastblock.hash,
            last_index=lastblock.index
        )
        manager.block = newblock 

