from network.constants import *
from network.peer import Peer
from network.requests import Type


# Assumption in this program:
# peer id's in this application are just "host:port" strings

class ExtendedPeer(Peer):

    def __init__(self, maxpeers, serverport, guid=None, serverhost=None, search=None):
        super(self.__class__, self).__init__(maxpeers, serverport, guid, serverhost)

        self.__search = search
        self.addrouter(self.__router)

        handlers = {
            Type.ROUTING_TABLE: self.__handle_cproutingtable,
            Type.PEERGUID: self.__handle_myguid,
            Type.PEERJOIN: self.__handle_addpeer,
            Type.PEERQUIT: self.__handle_peerquit,
        }
        for mt in handlers.keys():
            self.addhandler(mt, handlers[mt])


    def __router(self, peerid):
        if peerid not in self.getpeerids():
            # Cant route to peerId
            return [peerid, self.__search[:-4], self.__search[-4:]]
        else:
            return [peerid, *self.PEERS[peerid]]


    def __handle_addpeer(self, peerconn, data):
        self.peerlock.acquire()

        try:
            try:
                (peerid, host, port) = data.split()

                if self.maxpeersreached():
                    self.debugmsg('maxpeers {} reached: connection terminating'.format(self.maxpeers))
                    peerconn.send(Type.ROUTING_TABLE, 'Join: too many peers')
                    return False

                # peerid = '%s:%s'.format(host,port)
                if peerid not in self.getpeerids() and peerid != self.guid:
                    self.addpeer(peerid, host, port)
                    self.debugmsg('added peer: {}'.format(peerid))
                    peerconn.send(Type.REPLY, 'Join: peer added: {}'.format(peerid))
                else:
                    peerconn.send(Type.ROUTING_TABLE, 'Join: peer already inserted {}'.format(peerid))
            except:
                self.debugmsg('invalid insert {}: {}'.format(str(peerconn), data))
                peerconn.send(Type.ROUTING_TABLE, 'Join: incorrect arguments')
        finally:
            self.peerlock.release()


    def buildpeers(self, host, port, hops=1):
        """ buildpeers(host, port, hops) 
        ....Attempt to build the local peer list up to the limit stored by
        ....self.maxpeers, using a simple depth-first search given an
        ....initial host and port as starting point. The depth of the
        ....search is limited by the hops parameter.
        ...."""

        if self.maxpeersreached() or not hops:
            return

        peerid = None
        self.debugmsg('Building peers from ({},{})'.format(host, port))

        try:
            # returns an array of replies but we only expect one
            _, peerid = self.connectandsend(host, port, Type.PEERGUID, '')[0]

            self.debugmsg('contacted ' + peerid)
            resp = self.connectandsend(host, port, Type.PEERJOIN,
                    '{} {} {}'.format(self.guid, self.serverhost,
                    self.serverport))[0]
            self.debugmsg(str(resp))
            if resp[0] != Type.REPLY or peerid in self.getpeerids():
                return

            self.addpeer(peerid, host, port)

        # do recursive depth first search to add more peers

            resp = self.connectandsend(host, port, Type.ROUTING_TABLE, '',
                    pid=peerid)
            if len(resp) > 1:
                resp.reverse()
                resp.pop()  # get rid of header count reply
                while len(resp):
                    (nextpid, host, port) = resp.pop()[1].split()
                    if nextpid != self.guid:
                        self.buildpeers(host, port, hops - 1)
        except:
            if self.debug:
                traceback.print_exc()
            self.removepeer(peerid)



    def __handle_cproutingtable(self, peerconn, data):
        """ Handles the Type.ROUTING_TABLE message type. Message data is not used. """

        self.peerlock.acquire()
        try:
            self.debugmsg('Listing peers {}'.format(self.numberofpeers()))
            peerconn.send(Type.REPLY, '{}'.format(self.numberofpeers()))
            for pid in self.getpeerids():
                (host, port) = self.getpeer(pid)
                peerconn.send(Type.REPLY, '{} {} {}'.format(pid, host, port))
        finally:
            self.peerlock.release()


    def __handle_peerquit(self, peerconn, data):
        """ Handles the QUIT message type. The message data should be in the
        ....format of a string, "peer-id", where peer-id is the canonical
        ....name of the peer that wishes to be unregistered from this
        ....peer's directory.
        ...."""

        self.peerlock.acquire()
        try:
            peerid = data.strip()
            if peerid in self.getpeerids():
                msg = 'Quit: peer removed: {}'.format(peerid)
                self.debugmsg(msg)
                peerconn.send(Type.REPLY, msg)
                self.removepeer(peerid)
            else:
                msg = 'Quit: peer not found: {}'.format(peerid)
                self.debugmsg(msg)
                peerconn.send(Type.ROUTING_TABLE, msg)
        finally:
            self.peerlock.release()

    # precondition: may be a good idea to hold the lock before going
    #               into this function


    def __handle_myguid(self, peerconn, data):
        peerconn.send(Type.REPLY, self.guid)


    def main(self):
        socket = self.start()

        # if self.__search:
        #     self.search()
        
        self.loop(socket)


    # def search(self):
    #     host, port = self.__search[:-4], self.__search[-4:]
    #     self.debugmsg('Searching for Boot peer, connecting to {} {} {}'.format(self.guid, host, port))
    #     responses = self.send(self.__search, Type.PEERJOIN, '{} {} {}'.format(self.guid, self.serverhost, self.serverport))
    #     # responses = self.connectandsend(host, int(port), Type.PEERJOIN, '{} {} {}'.format(self.guid, self.serverhost, self.serverport))
    #     print(responses)
