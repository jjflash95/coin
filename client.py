# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
import os
import threading

from utils import getlastblock
from localstorage import LocalStorage
from p2p.peer import Peer

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

    def buildchains(self):
        thread = threading.Thread(target=self.p2p.buildchain)
        thread.start()
        return thread        

if __name__ == '__main__':
    storage = LocalStorage()
    client = Client(storage)
    client.buildp2p()
    client.listen()
    while True:
        print(client.transactionpool)
    
