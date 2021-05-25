from storage.storage import Storage
from p2p.network.constants import *
from p2p.network.enode import ExtendedNode
from p2p.network.requests import MSGType

from storage.models.models import ChainModel



class Peer(ExtendedNode):

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, storage=None, debug=0):
        self.storage = storage
        self.pool = None
        self.pending = set()
        self.startpendingroutine(self.__flushpendingpool, 3)

        super().__init__(maxpeers, serverport, guid=guid, serverhost=serverhost, debug=debug)

    def setpool(self, pool):
        self.pool = pool
        return self

    def getchain(self):
        return self.storage.getchain()

    def _gethandlers(self):
        handlers = super()._gethandlers()
        return {
            MSGType.GET_CHAIN: self.__handle_getchain,
            MSGType.TRANSACTION: self.__handle_newtransaction,
            **handlers
        }

    def __handle_getchain(self, peerconn, data):
        if self.storage is None:
            debug(self.output, 'Storage uninitialized')
            return
        try:
            debug(self.output, 'Sending chain!!')
            chain = self.getchain()
            debug(self.output, 'Sending chain of length: {}'.format(len(self.chain)))
            for block in chain.getblocks():
                peerconn.send(MSGType.PUT_CHAIN, block)
        except:
            if self.debug: traceback.print_exc()

    def __handle_newtransaction(self, peerconn, data):
        self.peerlock.acquire()
        self.pool.append(data)
        peerlist = [(peerid, peerdata) for peerid, peerdata in self.peers() if peerid != peerconn.id]
        self.propagate_transaction(MSGType.TRANSACTION, data, peerlist)
        self.peerlock.release()
        
    def propagate_transaction(self, transaction, peerlist=None):
        if transaction in self.pool:
            return
        if not peerlist and not self.peers():
            print('adding transaction to pending')
            self.pending.add(transaction)

        self.pool.append(transaction)
        self.propagate(MSGType.TRANSACTION, transaction, peerlist)

    def propagate(self, msgtype, msgdata, peerlist=None):
        if peerlist is None:
            peerlist = self.peers()

        for _, (host, port) in peerlist:
            self.connectandsend(host, port, msgtype, msgdata)
        
    def request_chain(self):
        for _, (host, port) in self.peers():
            chain = ''
            resp = self.connectandsend(host, port, MSGType.GET_CHAIN)
            for res in resp:
                chain += res[1]
            yield chain


    def startpendingroutine(self, clean, delay):
        """Tries to send pending transactions every <delay> seconds"""

        t = threading.Thread(target=self.__cleanpendingpool,
                             args=[clean, delay]).start()
    
    def __cleanpendingpool(self, clean, delay):
        while True:
            if self.pool is None: continue
            clean()
            time.sleep(delay)

    def __flushpendingpool(self):
        if not self.pool or not len(self.pool):
            return
        self.propagate_transaction(self.pool.pop())


