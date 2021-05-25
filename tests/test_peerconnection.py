# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
import unittest

from load_external import *
from load_external import Peer, LocalStorage
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

    def tearDown(self):
        import time
        time.sleep(.2)

    def getpeer(self, maxpeers=10):
        peer = Peer(maxpeers, self.currentport)
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
    
    # def testPeerRoutingTables(self):
    #     """
    #     THIS TEST ENSURES THAT ALL NODES BUILDING PEERS GET THE ROUTING
    #     TABLE FROM THE SERVER, AND START ASKING FOR EACH PEER OWN ROUTING
    #     TABLE TO BUILD THE ENTIRE NETWORK, AT LAST WE COMPARE EACH TABLE
    #     AND IT SHOULD HAVE ALL CONNECTIONS EXCEPT IT'S OWN.

    #     E.G: PEER 5002 SHOULD HAVE ALL 5000 ... 5004 EXCEPT PORT 5002
    #     """

    #     network = []
    #     peers = []
    #     threads = []
    #     numpeers = 5
    
    #     speer = self.getpeer(numpeers)
    #     shost = speer.serverhost
    #     sport = speer.serverport
    #     network.append((shost, sport))

    #     for _ in range(numpeers):
    #         peer = self.getpeer(numpeers)
    #         host = peer.serverhost
    #         port = peer.serverport
    #         peers.append(peer)
    #         network.append((host, port))


    #     st, speer = self.runserver(speer)
    #     for peer in peers:
    #         t, peer = self.runclient(peer, shost, sport)
    #         threads.append(t)

    #     speer.shutdown = True
    #     for peer in peers:
    #         peer.shutdown = True
        
    #     st.join()
    #     [t.join() for t in threads]

    #     for peer in [speer, *peers]:
    #         pnetwork = network.copy()
    #         peerconndata = (peer.serverhost, peer.serverport)
    #         pnetwork.remove(peerconndata)
    #         for _, conndata in peer.peertable.items():
    #             self.assertTrue(conndata in pnetwork)
    #         self.assertFalse(peerconndata in pnetwork)


    # def testMessagePropagation(self):
    #     """
    #     TEST ENSURES ALL NODES IN THE NETWORK RECEIVE THE PROPAGATED MSG
    #     """
    #     network = []
    #     threads = []
    #     peers = []
    #     peernum = 5
    
    #     speer = self.getpeer(peernum)
    #     shost = speer.serverhost
    #     sport = speer.serverport
    #     network.append((shost, sport))

    #     for _ in range(peernum):
    #         peer = self.getpeer(peernum)
    #         host = peer.serverhost
    #         port = peer.serverport
    #         peers.append(peer)
    #         network.append((host, port))
     
    #     t, speer = self.runserver(speer)
    #     threads.append(t)
    #     for peer in peers:
    #         t, peer = self.runclient(peer, shost, sport)
    #         threads.append(t)
        
    #     message = """{"id": "1", "message": "this is a message"}"""
    #     peers[0].propagate_transaction(message)

    #     speer.shutdown = True
    #     for peer in peers:
    #         peer.shutdown = True

    #     for t in threads:
    #         t.join()

    #     for peer in [speer, *peers]:
    #         self.assertEqual(len(peer.pool), 1)
    #         self.assertEqual(peer.pool[0], message)
        


    # def testMessagePropagateAndIgnoreIdenticalMessages(self):
    #     """
    #     TEST ENSURES ALL NODES IN THE NETWORK RECEIVE THE PROPAGATED MSG
    #     BUT IGNORE SUBSEQUENT SENDS OF SAME MSG
    #     """
    #     network = []
    #     threads = []
    #     peers = []
    #     peernum = 5
    
    #     speer = self.getpeer(peernum)
    #     shost = speer.serverhost
    #     sport = speer.serverport
    #     network.append((shost, sport))


    #     for _ in range(peernum):
    #         peer = self.getpeer(peernum)
    #         host = peer.serverhost
    #         port = peer.serverport
    #         peers.append(peer)
    #         network.append((host, port))
     
    #     t, speer = self.runserver(speer)
    #     threads.append(t)
    #     for peer in peers:
    #         t, peer = self.runclient(peer, shost, sport)
    #         threads.append(t)

    #     message = """{"id": "1", "message": "this is a duplicated message"}"""
    #     peers[0].propagate_transaction(message)
    #     peers[0].propagate_transaction(message)
    #     peers[0].propagate_transaction(message)

    #     speer.shutdown = True
    #     for peer in peers:
    #         peer.shutdown = True

    #     for t in threads:
    #         t.join()

    #     for peer in [speer, *peers]:
    #         self.assertEqual(len(peer.pool), 1)
    #         self.assertEqual(peer.pool[0], message)
        
    
    # def testPropagateReallyLongMessage(self):
    #     """
    #     THIS TEST ENSURES THAT ALL NODES BUILDING PEERS GET THE ROUTING
    #     TABLE FROM THE SERVER, AND START ASKING FOR EACH PEER OWN ROUTING
    #     TABLE TO BUILD THE ENTIRE NETWORK, AT LAST WE COMPARE EACH TABLE
    #     AND IT SHOULD HAVE ALL CONNECTIONS EXCEPT IT'S OWN.

    #     E.G: PEER 5002 SHOULD HAVE ALL 5000 ... 5004 EXCEPT PORT 5002
    #     """
    #     network = []
    #     threads = []
    #     peers = []
    #     peernum = 1
    
    #     speer = self.getpeer(peernum)
    #     shost = speer.serverhost
    #     sport = speer.serverport
    #     network.append((shost, sport))


    #     for _ in range(peernum):
    #         peer = self.getpeer(peernum)
    #         host = peer.serverhost
    #         port = peer.serverport
    #         peers.append(peer)
    #         network.append((host, port))
     
    #     t, speer = self.runserver(speer)
    #     threads.append(t)
    #     for peer in peers:
    #         t, peer = self.runclient(peer, shost, sport)
    #         threads.append(t)

    #     # 5.4 MB message
    #     message = """{"id": "1", "message": "this is a duplicated message"}"""*10
    #     for i in range(2):
    #         message = message*100

    #     peers[0].propagate_transaction(message)

    #     speer.shutdown = True
    #     for peer in peers:
    #         peer.shutdown = True

    #     for t in threads:
    #         t.join()

    #     for peer in [speer, *peers]:
    #         self.assertEqual(len(peer.pool), 1)
    #         self.assertEqual(peer.pool[0], message)
        

    # def testPropagateREALLYLongMessageWithSendChunks(self):
    #     """
    #     THIS TEST ENSURES THAT ALL NODES BUILDING PEERS GET THE ROUTING
    #     TABLE FROM THE SERVER, AND START ASKING FOR EACH PEER OWN ROUTING
    #     TABLE TO BUILD THE ENTIRE NETWORK, AT LAST WE COMPARE EACH TABLE
    #     AND IT SHOULD HAVE ALL CONNECTIONS EXCEPT IT'S OWN.

    #     E.G: PEER 5002 SHOULD HAVE ALL 5000 ... 5004 EXCEPT PORT 5002
    #     """
    #     network = []
    #     threads = []
    #     peers = []
    #     peernum = 1
    
    #     speer = self.getpeer(peernum)
    #     shost = speer.serverhost
    #     sport = speer.serverport
    #     network.append((shost, sport))


    #     for _ in range(peernum):
    #         peer = self.getpeer(peernum)
    #         host = peer.serverhost
    #         port = peer.serverport
    #         peers.append(peer)
    #         network.append((host, port))
     
    #     t, speer = self.runserver(speer)
    #     threads.append(t)
    #     for peer in peers:
    #         t, peer = self.runclient(peer, shost, sport)
    #         threads.append(t)

    #     # 5.4 MB message
    #     message = """{"id": "1", "message": "this is a duplicated message"}"""*10
    #     for i in range(2):
    #         message = message*100

    #     peers[0].propagate_transaction(message)

    #     speer.shutdown = True
    #     for peer in peers:
    #         peer.shutdown = True

    #     for peer in [speer, *peers]:
    #         self.assertEqual(len(peer.pool), 1)
    #         self.assertEqual(peer.pool[0], message)
        
    #     for t in threads:
    #         t.join()

    def testRequestForChainAndGetCorrectly(self):
        """
        THIS TEST ENSURES A NEW PEER CAN GET A FULL CHAIN
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

        storage = LocalStorage()
        fakestorage = LocalStorage(onmemory=True)
        speer.storage = storage
        
        for peer in peers:
            peer.storage = fakestorage
            for chain in peer.request_chain():
                print(chain)
    
        speer.shutdown = True
        for peer in peers:
            peer.shutdown = True

        import time
        time.sleep(2)

        for peer in [speer, *peers]:
            self.assertEqual(len(peer.pool), 1)
            # self.assertEqual(peer.pool[0], storage.get)
        
        for t in threads:
            t.join()


if __name__ == '__main__':
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    unittest.main()