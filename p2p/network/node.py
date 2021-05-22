from network.constants import *
from network.connection import P2PConnection
from network.requests import MSGType
from queue import Queue


class Node:
    PEERS = {}
    HANDLERS = {}
    QUEUE = Queue()

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, debug=1):
        self.debug = debug

        self.maxpeers = int(maxpeers)
        self.serverport = int(serverport)
        self.__resolveserverhost(serverhost)
        self.__resolvepeerid(guid)
        self.peerlock = threading.Lock()

        self.shutdown = False  
        self.router = None

    def __resolveserverhost(self, serverhost=None):
        """Search serverhost by connecting to google"""
        if not serverhost:
            tmpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmpsocket.connect(GOOGLE)
            serverhost = tmpsocket.getsockname()[0]
            tmpsocket.close()
        
        self.serverhost = serverhost

    def __resolvepeerid(self, guid=None):
        if not guid:
            guid = '{}{}'.format(self.serverhost, self.serverport)
        self.guid = guid


    def makeserversocket(self, port, maxqueue=5):
        """maxqueue is how many connections can be queued up"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # CHECK THIS
        # host = socket.gethostbyname(socket.gethostname())
        # print(host)
        s.bind(('', port))
        s.listen(maxqueue)
        return s

    def peers(self):
        for peerid, pdata in self.PEERS.items():
            yield (peerid, pdata)

    def send(self, peerid, msgtype, msgdata, waitresponse=True):
        if not self.router:
            raise Exception('Cant send message, no router')

        nextpid, host, port = self.router(peerid)
        if not nextpid:
            debug('Unable to route {} to {}'.format(msgtype, peerid))
            
        return self.__send(host, port, msgtype, msgdata, peerid=nextpid,
                        waitresponse=waitresponse)


    def __send(self, host, port, msgtype, msgdata, peerid=None, waitresponse=True):
        responses = []
        try:
            peerconn = P2PConnection(peerid, host, port, debug=self.debug)
            peerconn.send(msgtype, msgdata)
            debug('Sent {}: {}'.format(peerid, msgtype))
            
            if waitresponse:
                response = peerconn.receivedata()

            while (response != (None,None)):
                responses.append(response)
                debug('Got reply {}: {}'.format(peerid, str(responses)))
                response = peerconn.receivedata()
            peerconn.close()
        except KeyboardInterrupt:
            raise Exception('Ctrl+C')
        except:
            if self.debug:
                traceback.print_exc()
        
        return responses


    def getpeerids(self):
        return self.PEERS.keys()

    def setrouter(self, router):
        self.router = router

    def addpeer(self, peerid, host, port):
        """@return void"""
        if peerid in self.PEERS.keys():
            return
    
        if self.maxpeers and len(self.PEERS.keys()) >= self.maxpeers:
            return

        self.PEERS[peerid] = (host, int(port))

    def getpeer(self, peerid):
        if not peerid in self.PEERS:
            return (None, None)

        return self.PEERS[peerid]

    def startstabilizer(self, stabilizer, delay):
        """Runs stabilizer func every n seconds"""

        t = threading.Thread(target=self.__runstabilizer,
                             args=[stabilizer, delay]).start()


    def addhandler(self, msgtype, handler):
        assert len(msgtype) == MSGType.len()
        self.HANDLERS[msgtype] = handler


    def removepeers(self, peerids):
        if not type(peerids) == list:
            peerids = [peerids]

        for peerid in peerids:
            if peerid in self.PEERS.keys():
                del self.PEERS[peerid]


    def numberofpeers(self):
        return len(self.PEERS.keys())


    def maxpeersreached(self):
        if not self.maxpeers:
            return False

        return self.maxpeers > 0 and len(self.PEERS.keys()) >= self.maxpeers


    def checklivepeers(self):
        """ping all peers to check if they are still alive"""

        remove = []
        for pid in self.PEERS:
            isconnected = False
            try:
                debug('Check live {}'.format(pid))
                (host, port) = self.PEERS[pid]
                peer = P2PConnection(pid, host, port, debug=self.debug)
                peer.send('PING', '')
                isconnected = True
            except:
                remove.append(pid)
            if isconnected:
                peer.close()

        self.peerlock.acquire()
        try:
            self.removepeers(remove)
        finally:
            self.peerlock.release()


    def __runstabilizer(self, stabilizer, delay):
        while not self.shutdown:
            stabilizer()
            time.sleep(delay)


    def connectandsend(self, host, port, msgtype, msgdata='', pid=None, waitresponse=True):
        """ Returns an array of responses in
        format:
        [(response type, response data ),...]"""
    
        responses = []
        try:
            debug('Sending {}{}: {}'.format(host, port, msgtype))
            peerconn = P2PConnection(self.guid, host, port,
                    debug=self.debug)
            peerconn.send(msgtype, msgdata)
            debug('Sent {} => {}'.format(peerconn.id, msgtype))

            if waitresponse:
                reply = peerconn.receivedata()
                while reply != (None, None):
                    responses.append(reply)

                    debug('Got reply {}: {}'.format(pid,
                                    str(responses)))
                    reply = peerconn.receivedata()
            peerconn.close()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.debug:
                traceback.print_exc()

        return responses


    def main(self):
        serversocket = self.startserver()   
        self.loop(serversocket)


    def startserver(self):
        serversocket = self.makeserversocket(self.serverport)
        serversocket.settimeout(2)
        debug('Server started: {} ({}:{})'.format(
                                                    self.guid,
                                                    self.serverhost,
                                                    self.serverport))
        return serversocket


    def loop(self, serversocket):
        while not self.shutdown:
            try:
                if not self.QUEUE.empty():
                    self.__execute(*self.QUEUE.get())

                debug('Listening for connections...')
                clientsock, clientaddr = serversocket.accept()
                clientsock.settimeout(None)

                t = threading.Thread(target=self.__handlepeer,
                        args=[clientsock])
                t.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping main')
                self.shutdown = True
                continue
            except socket.timeout:
                # Nobody has connected to svport
                pass
            except Exception as e:
                if self.debug:
                    traceback.print_exc()
                    continue

        debug('Main loop exiting')
        serversocket.close()

    def __handlepeer(self, clientsock):
        debug('New child {}'.format(cthreadname()))
        debug('Connected {}'.format(str(clientsock.getpeername())))

        host, port = clientsock.getpeername()
        peerconn = P2PConnection(None, host, port, clientsock,
                                    debug=True)
        
        try:
            msgtype, msgdata = peerconn.receivedata()
            msgtype = msgtype.upper() if msgtype else ''
            if msgtype not in self.HANDLERS.keys():
                debug('Not handled: {}: {}'.format(msgtype, msgdata))
            else:
                debug('Handling peer msg: {}: {}'.format(msgtype,
                             msgdata))
                self.HANDLERS.get(msgtype)(peerconn, msgdata)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        debug('Disconnecting ' + str(clientsock.getpeername()))
        peerconn.close()

