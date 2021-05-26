from storage.models.models import BlockModel
from p2p.network.constants import *
from p2p.network.enode import ExtendedNode
from p2p.network.requests import MSGType
from events.events import Event
from encryption.block import Block
from encryption.transaction import Transaction




class Peer(ExtendedNode):

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, storage=None, emitter=None, debug=0):
        super(Peer, self).__init__(maxpeers, serverport, guid=guid, serverhost=serverhost, debug=debug)
        
        self.emitter = emitter
        self.storage = storage
        self.pool = []
        self.pending = set()
        self.startpendingroutine(self.__flushpendingpool, 3)

    def emit(self, event, data=None):
        if not self.emitter:
            return
        
        self.emitter.emit(event, data)

    def setpool(self, pool):
        self.pool = pool
        return self

    def getchain(self):
        return self.storage.getchain()
    
    def addchain(self, chain):
        return self.storage.addchain(chain)


    def _gethandlers(self):
        handlers = super()._gethandlers()
        return {
            MSGType.GET_CHAIN: self.__handle_getchain,
            MSGType.TRANSACTION: self.__handle_newtransaction,
            MSGType.BLOCK: self.__handle_newblock,
            **handlers
        }

    def __handle_getchain(self, peerconn, data):
        if self.storage is None:
            debug(self.output, 'Storage uninitialized')
            return
        try:
            chain = self.getchain()
            if not len(chain):
                return

            for block in chain.getblocks():
                peerconn.send(MSGType.PUT_CHAIN, block)
        except:
            traceback.print_exc()

    def __handle_newtransaction(self, peerconn, data):
        self.peerlock.acquire()
        try:
            transaction = Transaction.from_json(data)
        except:
            # Invalid or corrupted transaction
            return
        self.pool.append(transaction)
        if transaction in self.pool:
            return
    
        peerlist = [(peerid, peerdata) for peerid, peerdata in self.peers() if peerid != peerconn.id]
        self.propagate_transaction(transaction, peerlist)
        self.emit(Event.NEW_TRANSACTION)
        self.peerlock.release()

    def __handle_newblock(self, peerconn, data):
        self.peerlock.acquire()
        try:
            block = Block.from_json(data)
        except:
            # Invalid or corrupted block
            return
        if block in self.pool:
            return

        self.pool.append(block)
        peerlist = [(peerid, peerdata) for peerid, peerdata in self.peers() if peerid != peerconn.id]
        self.propagate_transaction(block, peerlist)
        self.emit(Event.NEW_BLOCK)
        self.peerlock.release()
        
    def propagate_transaction(self, transaction, peerlist=None):
        if type(transaction) == str:
            transaction = Transaction.from_json(transaction)
        if transaction in self.pool:
            return
        if not peerlist and not self.peers():
            self.pending.add(transaction)

        self.pool.append(transaction)
        self.propagate(MSGType.TRANSACTION, transaction.to_json(), peerlist)

    def propagate_block(self, block, peerlist=None):
        if type(block) == str:
            block = Block.from_json(block)
        if block in self.pool:
            return
        if not peerlist and not self.peers():
            self.pending.add(block)
        
        self.pool.append(block)
        self.propagate(MSGType.BLOCK, block.to_json(), peerlist)
            
    def propagate(self, msgtype, msgdata, peerlist=None):
        if peerlist is None:
            peerlist = self.peers()

        for _, (host, port) in peerlist:
            self.connectandsend(host, port, msgtype, msgdata)
        
    def request_chain(self):
        for _, (host, port) in self.peers():
            resp = self.connectandsend(host, port, MSGType.GET_CHAIN)
            chain = [res[1] for res in resp]
            chain = ','.join(chain)
            if chain: yield '[{}]'.format(chain)


    def startpendingroutine(self, clean, delay):
        """Tries to send pending transactions every <delay> seconds"""

        t = threading.Thread(target=self.__cleanpendingpool,
                             args=[clean, delay]).start()
    
    def __cleanpendingpool(self, clean, delay):
        while not self.shutdown:
            if self.pool is None: continue
            clean()
            time.sleep(delay)

    def __flushpendingpool(self):
        if not self.pool or not len(self.pool):
            return
        self.propagate_transaction(self.pool.pop())


