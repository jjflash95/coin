from network.constants import *




class P2PConnection(ThreadDebugging):
    def __init__(self, peerid, host, port, sock=None, debug=True):
        if not peerid:
            peerid = 'UNKNOWNGUID'
        self.id = peerid
        self.debug = debug
        self.s = sock

        if not self.s:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
            
        self.sd = self.s.makefile('rwb', None)


    def __makemessage(self, msgtype, msgdata):
        b = lambda s: bytes(s, 'utf-8')
        mlen = len(msgdata)
        return struct.pack('!4sL{}s'.format(mlen), b(msgtype), mlen, b(msgdata))


    def send(self, msgtype, msgdata):
        # print('making message', msgtype, msgdata)
        # msg = self.__makemessage(msgtype, msgdata)
        # print('made message: ', msg)
        # self.sd.write(msg)
        # self.sd.flush()
        try:
            msg = self.__makemessage(msgtype, msgdata)
            self.sd.write(msg)
            self.sd.flush()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            return False
        return True


    def receivedata(self):
        try:
            msgtype = self.sd.read(4)
            if not msgtype:
                return (None, None)

            lenstr = self.sd.read(4)
            msglen = int(struct.unpack('!L', lenstr)[0])
            msg = ''

            while len(msg) != msglen:
                data = self.sd.read(min(2048, msglen - len(msg)))
                if not len(data):
                    break
                msg += data

            if len(msg) != msglen:
                return (None, None)
        except KeyboardInterrupt:

            raise
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            return (None, None)

        return (msgtype.decode('utf-8'), msg)


    def close(self):
        self.s.close()
        self.s = None
        self.sd = None


    def __str__(self):
       return "|{}|".format(self.peerid)