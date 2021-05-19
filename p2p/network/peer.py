from network.constants import *
from network.connection import P2PConnection
from network.requests import Type


class Peer(ThreadDebugging):
    PEERS = {}
    HANDLERS = {}

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None):
        self.debug = 0

        self.maxpeers = int(maxpeers)
        self.serverport = int(serverport)
        self.__determineserverhost(serverhost)
        self.__determinepeerid(guid)
        self.peerlock = threading.Lock()

        self.shutdown = False  
        self.router = None

    def __determineserverhost(self, serverhost=None):
        """Search serverhost by connecting to google"""
        if not serverhost:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(GOOGLE)
            serverhost = s.getsockname()[0]
            s.close()
        
        self.serverhost = serverhost

    def __determinepeerid(self, guid=None):
        if not guid:
            guid = '{}{}'.format(self.serverhost, self.serverport)

        self.guid = guid


    def makeserversocket(self, port, backlog=5):
        """
        Backlog is how many connections can be queued up
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(backlog)
        return s


    def send(self, peerid, msgtype, msgdata, waitreply=True):
        if not self.router:
            self.debugmsg('There is no router func')
            return None

        nextpid, host, port = self.router(peerid)
        if not nextpid:
            self.debugmsg('Unable to route {} to {}'.format(msgtype, peerid))
            
        return self.__send(host, port, msgtype, msgdata, peerid=nextpid,
                        waitreply=waitreply)


    def __send(self, host, port, msgtype, msgdata, peerid=None, waitreply=True):
        msgreply = [] #replies
        try:
            peerconn = P2PConnection(peerid, host, port, debug=self.debug)
            self.debugmsg('Sending TO: {} -> {} {} {}: {}'.format(peerid, host, port, msgtype, msgdata))
            peerconn.send(msgtype, msgdata)
            self.debugmsg('Sent {}: {}' % (peerid, msgtype))
            
            if waitreply:
                onereply = peerconn.receivedata()

            while (onereply != (None,None)):
                msgreply.append(onereply)
                self.debugmsg('Got reply {}: {}'.format(peerid, str(msgreply)))
                onereply = peerconn.receivedata()
            peerconn.close()
        except KeyboardInterrupt:
            raise Exception('Ctrl+C')
        except:
            if self.debug:
                traceback.print_exc()
        
        return msgreply


    def getpeerids(self):
        return self.PEERS.keys()

    def addrouter(self, router):
        """ Registers a routing function with this peer. The setup of routing
        ....is as follows: This peer maintains a list of other known peers
        ....(in self.PEERS). The routing function should take the name of
        ....a peer (which may not necessarily be present in self.PEERS)
        ....and decide which of the known peers a message should be routed
        ....to next in order to (hopefully) reach the desired peer. The router
        ....function should return a tuple of three values: (next-peer-id, host,
        ....port). If the message cannot be routed, the next-peer-id should be
        ....None.
        ...."""

        self.router = router

    def addpeer(self, peerid, host, port):
        if peerid in self.PEERS.keys():
            return False
    
        if self.maxpeers and len(self.PEERS.keys()) >= self.maxpeers:
            return False

        self.PEERS[peerid] = (host, int(port))
        return True
        
    def startstabilizer(self, stabilizer, delay):
        """ Registers and starts a stabilizer function with this peer. 
        ....The function will be activated every <delay> seconds. """

        t = threading.Thread(target=self.__runstabilizer,
                             args=[stabilizer, delay]).start()


    def getpeer(self, peerid):
        assert peerid in self.peers  # maybe make this just a return NULL?
        return self.PEERS[peerid]


    def addhandler(self, msgtype, handler):
        assert len(msgtype) == Type.len()
        self.HANDLERS[msgtype] = handler


    def removepeer(self, peerid):
        if peerid in self.PEERS.keys():
            del self.peers[peerid]


    def numberofpeers(self):
        return len(self.PEERS.keys())


    def maxpeersreached(self):
        if not self.maxpeers:
            return False

        return self.maxpeers > 0 and len(self.PEERS.keys()) >= self.maxpeers


    def checklivepeers(self):
        """ Pings all current peers to see if they are still connected
        This function can be used as a simple stabilizer.
        """

        delete = []
        for pid in self.peers:
            isconnected = False
            try:
                self.debugmsg('Check live %s' % pid)
                (host, port) = self.peers[pid]
                peer = P2PConnection(pid, host, port, debug=self.debug)
                peer.send('PING', '')
                isconnected = True
            except:
                delete.append(pid)
            if isconnected:
                peer.close()

        self.peerlock.acquire()
        try:
            for pid in delete:
                if pid in self.peers:
                    del self.peers[pid]
        finally:
            self.peerlock.release()


    def __runstabilizer(self, stabilizer, delay):
        while not self.shutdown:
            stabilizer()
            time.sleep(delay)


    def connectandsend(self, host, port, msgtype, msgdata, pid=None, waitreply=True):
        """
        ....connectandsend( host, port, message type, message data, peer id,
        ....wait for a reply ) -> [ ( reply type, reply data ), ... ]

        ....Connects and sends a message to the specified host:port. The host's
        ....reply, if expected, will be returned as a list of tuples.
        ...."""
    

        msgreply = []

        self.debugmsg('Sending {}: {}'.format(pid, msgtype))
        peerconn = P2PConnection(pid, host, port,
                debug=self.debug)
        peerconn.send(msgtype, msgdata)
        self.debugmsg('Sent {}: {}'.format(peerconn.id, msgtype))

        if waitreply:
            print('waiting reply')
            reply = peerconn.receivedata()
            while reply != (None, None):
                print('still waiting...')

                msgreply.append(reply)
                self.debugmsg('Got reply {}: {}' % (pid,
                                str(msgreply)))
                reply = peerconn.receivedata()
        peerconn.close()


        print(msgreply)
        return msgreply
        # msgreply = []
        # try:
        #     peerconn = P2PConnection(pid, host, port,
        #             debug=self.debug)
        #     peerconn.send(msgtype, msgdata)
        #     self.debugmsg('Sent {}: {}'.format(pid, msgtype))

        #     if waitreply:
        #         reply = peerconn.receivedata()
        #         while reply != (None, None):
        #             msgreply.append(reply)
        #             self.debugmsg('Got reply {}: {}' % (pid,
        #                          str(msgreply)))
        #             reply = peerconn.receivedata()
        #     peerconn.close()
        # except KeyboardInterrupt:
        #     raise
        # except Exception as e:
        #     if self.debug:
        #         traceback.print_exc()

        # return msgreply


    def start(self):
        s = self.makeserversocket(self.serverport)
        s.settimeout(2)
        self.debugmsg('Server started: {} ({}:{})'.format(
                                                    self.guid,
                                                    self.serverhost,
                                                    self.serverport))
        return s


    def loop(self, s):
        while not self.shutdown:

            try:
                self.debugmsg('Listening for connections...')
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(None)

                t = threading.Thread(target=self.__handlepeer,
                        args=[clientsock])
                t.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping main')
                self.shutdown = True
                continue
            except Exception as e:
                if self.debug:
                    traceback.print_exc()
                    continue

        self.debugmsg('Main loop exiting')
        s.close()


    def __handlepeer(self, clientsock):
        self.debugmsg('New child {}'.format(str(threading.currentThread().getName())))
        self.debugmsg('Connected {}'.format(str(clientsock.getpeername())))

        host, port = clientsock.getpeername()
        peerconn = P2PConnection(None, host, port, clientsock,
                                    debug=True)

        msgtype, msgdata = peerconn.receivedata()
        msgtype = msgtype.upper() if msgtype else ''
        print(msgdata, msgtype)
        if msgtype not in self.HANDLERS.keys():
            self.debugmsg('Not handled: {}: {}'.format(msgtype, msgdata))
        else:
            self.debugmsg('Handling peer msg: {}: {}'.format(msgtype,
                            msgdata))
            self.HANDLERS.get(msgtype)(peerconn, msgdata)
        try:
            msgtype, msgdata = peerconn.receivedata()
            msgtype = msgtype.upper() if msgtype else ''
            print(msgtype)
            if msgtype not in self.HANDLERS.keys():
                self.debugmsg('Not handled: {}: {}'.format(msgtype, msgdata))
            else:
                self.debugmsg('Handling peer msg: {}: {}'.format(msgtype,
                             msgdata))
                self.HANDLERS.get(msgtype)(peerconn, msgdata)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        self.debugmsg('Disconnecting ' + str(clientsock.getpeername()))
        peerconn.close()

