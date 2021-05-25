import sys
from queue import Queue

from p2p.network.connection import P2PConnection
from p2p.network.constants import *
from p2p.network.requests import MSGType


class Node:
    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, debug=0):
        self.peertable = {}
        self.handlers = {}
        self.queue = Queue()

        self.debug = debug
        self.output = sys.stdout

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
        try:
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
        except OSError:
            """PORT IS OCCUPIED, TRYING TO BUILD FROM NEXT PORT"""
            try:
                s.close()
            except:
                pass
            return self.makeserversocket(port + 1, maxqueue)
        self.serverport = port
        return s

    def peers(self):
        for peerid, pdata in self.peertable.items():
            yield (peerid, pdata)

    def send(self, peerid, msgtype, msgdata, waitresponse=True):
        if not self.router:
            raise Exception('Cant send message, no router')

        nextpid, host, port = self.router(peerid)
        if not nextpid:
            debug(self.output, 'Unable to route {} to {}'.format(msgtype, peerid))
            
        return self.__send(host, port, msgtype, msgdata, peerid=nextpid,
                        waitresponse=waitresponse)


    def __send(self, host, port, msgtype, msgdata, peerid=None, waitresponse=True):
        responses = []

        peerconn = P2PConnection(peerid, host, port, debug=self.debug)
        try:
            peerconn.send(msgtype, msgdata)
            debug(self.output, 'Sent {}: {}'.format(peerid, msgtype))
            
            if waitresponse:
                response = peerconn.receivedata()

            while (response != (None,None)):
                responses.append(response)
                debug(self.output, 'Got reply {}: {}'.format(peerid, str(responses)))
                response = peerconn.receivedata()
            peerconn.close()
        except KeyboardInterrupt:
            raise Exception('Ctrl+C')
        except:
            if self.debug:
                traceback.print_exc()
        
        return responses


    def getpeerids(self):
        return self.peertable.keys()

    def setrouter(self, router):
        self.router = router

    def addpeer(self, peerid, host, port):
        """@return void"""
        if peerid in self.peertable.keys():
            return
    
        if self.maxpeers and len(self.peertable.keys()) >= self.maxpeers:
            return

        self.peertable[peerid] = (host, int(port))

    def getpeer(self, peerid):
        if not peerid in self.peertable:
            return (None, None)

        return self.peertable[peerid]

    def startstabilizer(self, stabilizer, delay):
        """Runs stabilizer func every n seconds"""

        t = threading.Thread(target=self.__runstabilizer,
                             args=[stabilizer, delay]).start()


    def addhandler(self, msgtype, handler):
        assert len(msgtype) == MSGType.len()
        self.handlers[msgtype] = handler


    def removepeers(self, peerids):
        if not type(peerids) == list:
            peerids = [peerids]

        for peerid in peerids:
            if peerid in self.peertable.keys():
                del self.peertable[peerid]


    def numberofpeers(self):
        return len(self.peertable.keys())


    def maxpeersreached(self):
        if not self.maxpeers:
            return False

        return self.maxpeers > 0 and len(self.peertable.keys()) >= self.maxpeers


    def checklivepeers(self):
        """ping all peers to check if they are still alive"""

        remove = []
        for pid in self.peertable:
            isconnected = False
            try:
                debug(self.output, 'Check live {}'.format(pid))
                (host, port) = self.peertable[pid]
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
        debug(self.output, 'Sending {}{}: {}'.format(host, port, msgtype))
        peerconn = P2PConnection(self.guid, host, port,
                debug=self.debug)
        try:
            peerconn.send(msgtype, msgdata)
            debug(self.output, 'Sent {} => {}'.format(peerconn.id, msgtype))

            if waitresponse:
                reply = peerconn.receivedata()
                while reply != (None, None):
                    responses.append(reply)

                    debug(self.output, '[ConnAndSend] Got reply from "{}": {}'.format(pid,
                                    str(responses)))
                    reply = peerconn.receivedata()
        except KeyboardInterrupt:
            raise
        except Exception:
            if self.debug:
                traceback.print_exc()
        finally:
            peerconn.close()

        return responses


    def main(self):
        serversocket = self.startserver()   
        self.loop(serversocket)


    def startserver(self):
        serversocket = self.makeserversocket(self.serverport)
        serversocket.settimeout(2)
        debug(self.output, 'Server started: {} ({}:{})'.format(
                                                    self.guid,
                                                    self.serverhost,
                                                    self.serverport))
        return serversocket


    def loop(self, serversocket):
        while not self.shutdown:
            try:
                if not self.queue.empty():
                    self.__execute(*self.queue.get())

                debug(self.output, 'Listening for connections...')
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
            except Exception:
                if self.debug:
                    traceback.print_exc()
                    continue

        debug(self.output, 'Main loop exiting')
        serversocket.close()

    def __handlepeer(self, clientsock):
        debug(self.output, 'New child {}'.format(cthreadname()))
        debug(self.output, 'Connected {}'.format(str(clientsock.getpeername())))

        host, port = clientsock.getpeername()
        peerconn = P2PConnection(None, host, port, clientsock,
                                    debug=True)
        
        try:
            msgtype, msgdata = peerconn.receivedata()
            msgtype = msgtype.upper() if msgtype else ''
            if msgtype not in self.handlers.keys():
                debug(self.output, 'Not handled: {}: {}'.format(msgtype, msgdata))
            else:
                debug(self.output, 'Handling peer msg: {}: {}...'.format(msgtype,
                             msgdata[:70]))
                self.handlers.get(msgtype)(peerconn, msgdata)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        debug(self.output, 'Disconnecting ' + str(clientsock.getpeername()))
        peerconn.close()

