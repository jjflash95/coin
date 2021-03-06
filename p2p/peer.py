from p2p.bfilter import BloomFilter
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
        
        self.filter = BloomFilter(self.guid)
        self.emitter = emitter
        self.storage = storage
        self.pool = []
        self.pending = set()
        self.startroutine(self.__cleanpendingpool, self.__flushpendingpool, 3)
        self.startroutine(self.__getpeercount, self.__countpeers, 120)
        self.startroutine(self.__updateblockchain, self.__requestchain, 120)

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

            if not chain or not len(chain):
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
        self.emit(Event.NEWTRANSACTION)
        self.peerlock.release()

    def __handle_newblock(self, peerconn, data):
        self.peerlock.acquire()
        try:
            block = Block.from_json(data)
        except:
            debug(self.output, 'Unable to serialize block')
            if self.debug:
                traceback.print_exc()
            # Invalid or corrupted block
            return
        if block in self.pool:
            debug(self.output, 'Block is currently on pool')
            return

        self.pool.append(block)
        peerlist = [(peerid, peerdata) for peerid, peerdata in self.peers() if peerid != peerconn.id]
        self.propagate_block(block, peerlist)
        self.emit(Event.NEWBLOCK)
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
        

    def startroutine(self, loop, routine, delay):
        t = threading.Thread(target=loop,
                             args=[routine, delay], daemon=True).start()

    # def startpendingroutine(self, clean, delay):
    #     """Tries to send pending transactions every <delay> seconds"""

    #     t = threading.Thread(target=self.__cleanpendingpool,
    #                          args=[clean, delay], daemon=True).start()

    # def startpeercountroutine(self, countpeers, delay):
    #     """Updates current peers connected to the network every <delay> s"""
        
    #     t = threading.Thread(target=self.__getpeercount,
    #                          args=[countpeers, delay], daemon=True).start()

    # def startupdatechainrequest(self, updatechain, delay):
    #     """Updates entire chain to keep consistency"""
    #     t = threading.Thread(target=self.__requestchain,
    #                         args=[updatechain, delay], daemon=True).start()


    def __updateblockchain(self, requestchain, delay):
        while not self.shutdown:
            requestchain()
            time.sleep(delay)

    def requestchain(self):
        for c in self.__requestchain():
            yield c
            
    def __requestchain(self):
        for _, (host, port) in self.peers():
            resp = self.connectandsend(host, port, MSGType.GET_CHAIN)
            chain = [res[1] for res in resp]
            chain = ','.join(chain)
            if chain:
                chain = '[{}]'.format(chain)
                self.emit(Event.NEWCHAIN, chain)
                yield chain

    def __getpeercount(self, countpeers, delay):
        while not self.shutdown:
            pc = countpeers()
            if self.emitter:
                self.emit(Event.PEERCOUNT, pc)
            self.propagate(MSGType.PEERCOUNT, pc)
            time.sleep(delay)

    def __countpeers(self):
        # TO DO, implement bloom filter
        return 2
    
    def __cleanpendingpool(self, clean, delay):
        while not self.shutdown:
            if self.pool is None: continue
            clean()
            time.sleep(delay)

    def __flushpendingpool(self):
        if not self.pool or not len(self.pool):
            return
        self.propagate_transaction(self.pool.pop())


