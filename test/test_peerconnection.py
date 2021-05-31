# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
import unittest

from test.load_external import *
from test.load_external import (Peer, LocalStorage, MSGType,
    Transaction, validtransaction, Block, BlockChain,
    send, coinbase, getkey, recid, validblockchain)
import random
import threading
import warnings



class TestPeerConnection(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK THAT PEER CONNECTIONS
    WORK AS INTENDED, ROUTING EACH PEER INTO OTHERS, ASWELL
    AS SENDING AND RECEIVING DATA FROM PEERS,
    MAYBE LATER ADD LONG SEQUENCES OF DATA TO BE TRANSFERED
    """
    currentport = 9000
    challenge = 2

    def getpeer(self, maxpeers=10, output=False):
        peer = Peer(maxpeers, self.currentport)
        if not output:
            peer.debug = 0
            peer.output = None
        self.currentport = peer.serverport + 1
        return peer

    def runserver(self, peer):
        t = threading.Thread(target=peer.main)
        t.start()
        return t, peer
    

    def runclient(self, peer, shost, sport):
        t = threading.Thread(target=peer.main)
        t.start()
        peer.buildpeers(shost, int(sport))
        return t, peer
        
    def makeblock(self, pk, last_hash, last_index):
        return Block(coinbase(pk), last_hash, last_index)

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)
    
    def makechain(self, pk):
        genesis = self.makeblock(pk, '0', 0)
        genesis.calculate_hash()
        return BlockChain([genesis])
    
    def testPeerRoutingTables(self):
        """
        THIS TEST ENSURES THAT ALL NODES BUILDING PEERS GET THE ROUTING
        TABLE FROM THE SERVER, AND START ASKING FOR EACH PEER OWN ROUTING
        TABLE TO BUILD THE ENTIRE NETWORK, AT LAST WE COMPARE EACH TABLE
        AND IT SHOULD HAVE ALL CONNECTIONS EXCEPT IT'S OWN.

        E.G: PEER 5002 SHOULD HAVE ALL 5000 ... 5004 EXCEPT PORT 5002
        """

        network = []
        peers = []
        numpeers = 5
    
        speer = self.getpeer(numpeers)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))

        for _ in range(numpeers):
            peer = self.getpeer(numpeers)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))


        st, speer = self.runserver(speer)
        for peer in peers:
            _, peer = self.runclient(peer, shost, sport)

        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        for peer in [speer, *peers]:
            pnetwork = network.copy()
            peerconndata = (peer.serverhost, peer.serverport)
            pnetwork.remove(peerconndata)
            for guid, conndata in peer.peertable.items():
                self.assertTrue(conndata in pnetwork)
            self.assertFalse(peerconndata in pnetwork)


    def testMessagePropagation(self):
        """
        TEST ENSURES ALL NODES IN THE NETWORK RECEIVE THE PROPAGATED MSG
        """
        network = []
        threads = []
        peers = []
        peernum = 5
    
        speer = self.getpeer(peernum)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))

        for _ in range(peernum):
            peer = self.getpeer(peernum)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))
     
        t, speer = self.runserver(speer)
        threads.append(t)
        for peer in peers:
            t, peer = self.runclient(peer, shost, sport)
            threads.append(t)
        
        transaction = Transaction.from_json(validtransaction())
        peers[0].propagate_transaction(transaction)

        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        for peer in [speer, *peers]:
            self.assertEqual(len(peer.pool), 1)
            self.assertEqual(peer.pool[0], transaction)
        
        for t in threads:
            t.join()


    def testMessagePropagateAndIgnoreIdenticalMessages(self):
        """
        TEST ENSURES ALL NODES IN THE NETWORK RECEIVE THE PROPAGATED MSG
        BUT IGNORE SUBSEQUENT SENDS OF SAME MSG
        """
        network = []
        threads = []
        peers = []
        peernum = 5
    
        speer = self.getpeer(peernum)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))


        for _ in range(peernum):
            peer = self.getpeer(peernum)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))
     
        t, speer = self.runserver(speer)
        threads.append(t)
        for peer in peers:
            t, peer = self.runclient(peer, shost, sport)
            threads.append(t)

        transaction = Transaction.from_json(validtransaction())
        peers[0].propagate_transaction(transaction)
        peers[0].propagate_transaction(transaction)
        peers[0].propagate_transaction(transaction)

        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        for peer in [speer, *peers]:
            self.assertEqual(len(peer.pool), 1)
            self.assertEqual(peer.pool[0], transaction)
        
        for t in threads:
            t.join()
    
    def testPropagateReallyLongChain(self):
        """
        TEST PROPAGATION OF FULL BLOCK (TRANSACTION LIMIT)
        """
        network = []
        threads = []
        peers = []
        peernum = 1
    
        speer = self.getpeer(peernum)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))


        for _ in range(peernum):
            peer = self.getpeer(peernum)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))
     
        t, speer = self.runserver(speer)
        threads.append(t)
        for peer in peers:
            t, peer = self.runclient(peer, shost, sport)
            threads.append(t)

        sk, pk = getkey()
        block = self.makeblock(pk, '0', 0)
        for i in range(30):
            block.add(send(sk, pk, recid(), random.random()))
        
        block.calculate_hash()
        peers[0].propagate_block(block)
        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        for peer in [speer, *peers]:
            self.assertEqual(len(peer.pool), 1)
            self.assertEqual(peer.pool[0], block)
        
        for t in threads:
            t.join()

    def testRequestForChainAndGetCorrectly(self):
        """
        THIS TEST ENSURES A NEW PEER CAN GET A FULL CHAIN
        """
        network = []
        threads = []
        peers = []
        peernum = 3
    
        speer = self.getpeer(peernum)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))

        for _ in range(peernum):
            peer = self.getpeer(peernum)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))
     
        t, speer = self.runserver(speer)
        threads.append(t)
        for peer in peers:
            t, peer = self.runclient(peer, shost, sport)
            threads.append(t)

        storage = LocalStorage(path=False)
        speer.storage = storage

        for peer in peers:
            fakestorage = LocalStorage(path=False)
            peer.storage = fakestorage
            for chain in peer.requestchain():
                if not chain:
                    continue
                peer.addchain(chain)
    
        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        for peer in [speer, *peers]:
            self.assertEqual(speer.getchain(), peer.getchain())
            self.assertEqual(speer.storage.getchain(), peer.storage.getchain())
        
        for t in threads:
            t.join()

    def testRequestReallyLongChain(self):
        """
        THIS TEST ENSURES A NEW PEER CAN GET A FULL CHAIN
        """
        network = []
        threads = []
        peers = []
        peernum = 1
    
        speer = self.getpeer(maxpeers=peernum, output=False)
        shost = speer.serverhost
        sport = speer.serverport
        network.append((shost, sport))

        for _ in range(peernum):
            peer = self.getpeer(maxpeers=peernum, output=False)
            host = peer.serverhost
            port = peer.serverport
            peers.append(peer)
            network.append((host, port))
     
        t, speer = self.runserver(speer)
        threads.append(t)

        for peer in peers:
            t, peer = self.runclient(peer, shost, sport)
            threads.append(t)

        fakestorage = LocalStorage(path=False)
        speer.storage = fakestorage

        # make chain
        sk, pk = getkey()
        chain = self.makechain(pk)

        # print('BUILDING BLOCKS')
        for i in range(1):
            # print('BLOCK {} OF 30'.format(i))
            block = self.makeblock(pk, chain.get_last_hash(), chain.get_last_index())
            for i in range(Block.__limit__):
                block.add(self.maketransaction(sk, pk, recid()))
            
            block.calculate_hash()
            chain.add(block)
        speer.storage.addchain(chain)

        for peer in peers:
            peer.storage = LocalStorage(path=False)
            for chain in peer.requestchain():
                if not chain:
                    continue
                peer.addchain(chain)
    
        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        pchain = speer.getchain()
        for peer in [speer, *peers]:
            self.assertEqual(pchain, peer.getchain())
            self.assertEqual(speer.storage.getchain(), peer.storage.getchain())
        
        for t in threads:
            t.join()        



if __name__ == '__main__':
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    unittest.main()
