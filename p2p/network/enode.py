from p2p.network.constants import *
from p2p.network.node import Node
from p2p.network.requests import MSGType



class ExtendedNode(Node):

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, debug=0):
        super(ExtendedNode, self).__init__(maxpeers, serverport, guid, serverhost, debug=debug)

        self.setrouter(self.__router)

        handlers = self._gethandlers()
        for mt in handlers.keys():
            self.addhandler(mt, handlers[mt])


    def buildpeers(self, host, port, depth=30):
        """Builds peers from given host, by asking for his routing
        table and recursively adding all peers until reaching maximum
        peers or max recursive depth (determined by depth variable)"""

        if self.maxpeersreached() or not depth:
            return

        debug(self.output, 'Building peers from ({},{})'.format(host, port))

        peerid = '{}:{}'.format(host, port)

        try:
            # returns an array of replies but we only expect one
            _, peerid = self.connectandsend(host, port, MSGType.PEERGUID, '')[0]

            debug(self.output, 'contacted ' + peerid)
            resp = self.connectandsend(host, port, MSGType.PEERJOIN,
                    '{} {} {}'.format(self.guid, self.serverhost,
                    self.serverport))[0]

            # if that peer does not respond or i already have his GUID added
            if resp[0] != MSGType.REPLY or peerid in self.getpeerids():
                return

            self.addpeer(peerid, host, port)

            # once a peer is added, I request his routing table
            resp = self.connectandsend(host, port, MSGType.ROUTING_TABLE, '', pid=peerid)

            assert len(resp) > 1
            
            pnum = resp[0]
            resp = resp[1:]
            debug(self.output, 'got routing table with {} peers'.format(pnum))
            for res in resp:
                (nextpid, host, port) = res[1].split()
                if nextpid == self.guid:
                    continue
    
                self.buildpeers(host, port, depth - 1)
        except socket.error:
            self.removepeers(peerid)
        except Exception:
            if self.debug:
                traceback.print_exc()
        
            self.removepeers(peerid)


    def __router(self, peerid):
        if peerid not in self.getpeerids():
            return (None, None, None)
 
        return [peerid, *self.peertable[peerid]]

    def _gethandlers(self):
        return {
            MSGType.ROUTING_TABLE: self.__handle_cproutingtable,
            MSGType.PEERGUID: self.__handle_myguid,
            MSGType.PEERJOIN: self.__handle_addpeer,
            MSGType.PEERQUIT: self.__handle_peerquit,
        }

    def __handle_addpeer(self, peerconn, data):
        try:
            self.peerlock.acquire()
            peerid, host, port = data.split()

            if self.maxpeersreached():
                debug(self.output, 'maxpeers {} reached: connection terminating'.format(self.maxpeers))
                peerconn.send(MSGType.ROUTING_TABLE, 'JOIN: connection refused, too many peers')

            if peerid not in self.getpeerids() and peerid != self.guid:
                self.addpeer(peerid, host, port)
                debug(self.output, 'added peer: {}'.format(peerid))
                peerconn.send(MSGType.REPLY, 'JOIN: added peer: {}'.format(peerid))
            else:
                peerconn.send(MSGType.ROUTING_TABLE, 'JOIN: peer already in table {}'.format(peerid))
        except:
            debug(self.output, 'Can\'t add peer {}: {}'.format(str(peerconn), data))
            peerconn.send(MSGType.ROUTING_TABLE, 'Join: incorrect arguments')
        finally:
            self.peerlock.release()

    def __handle_cproutingtable(self, peerconn, data):
        """ Handles MSGType.ROUTING_TABLE. Message data is not used."""

        self.peerlock.acquire()
        try:
            debug(self.output, 'Listing peers {}'.format(self.numberofpeers()))
            peerconn.send(MSGType.REPLY, '{}'.format(self.numberofpeers()))
            for pid in self.getpeerids():
                (host, port) = self.getpeer(pid)
                peerconn.send(MSGType.REPLY, '{} {} {}'.format(pid, host, port))
        finally:
            self.peerlock.release()


    def __handle_peerquit(self, peerconn, data):
        """ Handles MSGType.QUIT. data is string "peerid" to get removed"""
        self.peerlock.acquire()
        try:
            peerid = data.strip()
            if peerid in self.getpeerids():
                self.removepeers(peerid)
                peerconn.send(MSGType.REPLY, 'QUIT: peer removed: {}'.format(peerid))
        finally:
            self.peerlock.release()

    def __handle_myguid(self, peerconn, data):
        peerconn.send(MSGType.REPLY, self.guid)


