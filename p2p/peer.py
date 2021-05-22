from network.constants import *
from network.enode import ExtendedNode
from network.requests import MSGType
import json



class Peer(ExtendedNode):

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None):
        self.chain = None
        self.pool = []

        super().__init__(maxpeers, serverport, guid=guid, serverhost=serverhost)

    def setpool(self, pool):
        self.pool = pool
        return self

    def setchain(self, chain):
        self.chain = chain
        return self

    def _gethandlers(self):
        handlers = super()._gethandlers()
        return {
            MSGType.GET_CHAIN: self.__handle_getchain,
            MSGType.TRANSACTION: self.__handle_newtransaction,
            **handlers
        }

    def __handle_getchain(self, peerconn, data):
        if self.chain is None:
            return
        try:
            peerconn.send(MSGType.REPLY, self.chain)
        except:
            if self.debug: traceback.print_exc()

    def __handle_newtransaction(self, peerconn, data):
        self.peerlock.acquire()
        self.pool.append(json.loads(data))
        peerlist = [(peerid, peerdata) for peerid, peerdata in self.peers() if peerid != peerconn.id]
        self.propagate(data, peerlist)
        self.peerlock.release()
    
    def propagate(self, transaction, peerlist=None):
        transaction = json.loads(transaction)
        if transaction['id'] in [t['id'] for t in self.pool]:
            return

        self.pool.append(transaction)
        if peerlist is None:
            peerlist = self.peers()

        for _, (host, port) in peerlist:
            self.connectandsend(host, port, MSGType.TRANSACTION, json.dumps(transaction, sort_keys=True))
        
    def getchain(self):
        for _, (host, port) in self.peers():
            chain = ''
            resp = self.connectandsend(host, port, MSGType.GET_CHAIN)
            for res in resp:
                chain += res[1]
            yield chain

