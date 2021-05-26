from p2p.network.constants import *


class TransferSocket:
    def __init__(self, socket):
        self.socket = socket.makefile('rwb', None)

    def __makemessage(self, msgtype, msgdata):
        b = lambda s: bytes(s, 'utf-8')
        mlen = len(msgdata)
        return struct.pack('!4sL{}s'.format(mlen), b(msgtype), mlen, b(msgdata))

    def send(self, msgtype, msgdata):
        msg = self.__makemessage(msgtype, msgdata)
        self.socket.write(msg)
        self.socket.flush()
    
    def receivedata(self):
        msgtype = self.socket.read(4)
        if not msgtype:
            return (None, None)

        lenstr = self.socket.read(4)
        msglen = int(struct.unpack('!L', lenstr)[0])
        msg = ''

        while len(msg) != msglen:
            data = self.socket.read(min(2048, msglen - len(msg)))
            if not len(data): break
            msg += data.decode('utf-8')

        if len(msg) != msglen:
            return (None, None)
    
        return (msgtype.decode('utf-8'), msg)



class P2PConnection:
    def __init__(self, peerid, host, port, sock=None, debug=True):
        self.id = peerid if peerid else 'UNKNOWNGUID'
        self.debug = debug
        self.socket = sock

        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, int(port)))
            
        self.tsocket = TransferSocket(self.socket)

    def send(self, msgtype, msgdata):
        try:
            if type(msgdata) != str:
                msgdata = str(msgdata)

            self.tsocket.send(msgtype, msgdata)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            return False
        return True


    def receivedata(self):
        try:
            return self.tsocket.receivedata()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            return (None, None)

    def close(self):
        self.socket.close()
        self.socket = None
        self.tsocket = None


    def __str__(self):
       return "[{}]".format(self.peerid)