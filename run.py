import os

from client import Client
from config import buildconfig
from events.blockmanager import BlockManager
from events.emitter import Emitter
from localstorage import LocalStorage

CONFIG = buildconfig()

KEYS_PATH = CONFIG['keys']['path']
DB_PATH = CONFIG['db']['path']

SERVERPORT = CONFIG['p2p']['serverport']
MAXPEERS = CONFIG['p2p']['maxpeers']
BUILDFROM = CONFIG['p2p']['buildfrom']
GUID = CONFIG['p2p']['guid']

os.environ['DEBUGMODE'] = CONFIG['client']['debugmode']


if __name__ == '__main__':
    storage = LocalStorage(DB_PATH)
    client = Client(
        keyspath=KEYS_PATH,
        maxpeers=MAXPEERS,
        serverport=SERVERPORT,
        storage=storage)

    client.buildfrom = BUILDFROM.split()
    client.buildp2p()
    client.listen()
    client.p2p.output = None
    
    newblock = client.newblock()
    manager = BlockManager(client.public, newblock, storage)
    emitter = Emitter()
    emitter.register(manager)
    client.p2p.emitter = emitter

    while True:
        print('calculating hash...')
        newblock.calculate_hash()
        storage.addblock(newblock)
        client.p2p.propagate_block(newblock)
        lastblock = newblock
        newblock = client.newblock()
        manager.block = newblock 

