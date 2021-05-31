# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
import os
import threading

from p2p.peer import Peer
from encryption.keys.keys import PrivateKey, PublicKey
from encryption.generate import coinbase, send, block, chain
from encryption.block import Block


class Client:
    def __init__(self, keyspath, maxpeers, serverport, storage):
        self.secret = PrivateKey(keyspath)
        self.public = PublicKey(keyspath)
        self.storage = storage
        self.maxpeers = maxpeers
        self.serverport = serverport
        self.buildfrom = []
 
    def buildp2p(self):
        self.transactionpool = []
        p2p = Peer(
            self.maxpeers,
            self.serverport,
            storage=self.storage)
        p2p.pool = self.transactionpool
        p2p.storage = self.storage
        peers = [p.split(':') for p in self.buildfrom if p]
        for (host, port) in peers:
            p2p.buildpeers(host, int(port))
        
        self.p2p = p2p

    def listen(self):
        thread = threading.Thread(target=self.p2p.main)
        thread.start()
        return thread
    
    def lastblock(self):
        hollowchain = self.storage.getchain(buildcascade=False)
        if not hollowchain:
            return False
        
        return hollowchain[-1]

    def getchain(self):
        chain = self.storage.getchain(buildcascade=True)
        if not chain:
            chain = self.newchain()
        return chain

    def haschain(self):
        print(self.storage.haschain())
        return self.storage.haschain()

    def newblock(self):
        chain = self.getchain()
        lasthash = chain.get_last_hash()
        lastindex = chain.get_last_index()
        return block(self.public, lasthash, lastindex)
    
    def newtransaction(self, recipientid, amount):
        return send(self.secret, self.public, recipientid, amount)
    
    def newchain(self):
        return chain()
