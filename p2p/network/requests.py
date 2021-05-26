

class MSGType():
    PEERGUID = 'GUID'
    ROUTING_TABLE = 'CPRT'
    PEERJOIN = 'JOIN'
    PEERQUIT = 'QUIT'

    REPLY = 'REPL'
    ERROR = 'ERRO'

    GET_CHAIN = 'GTCH'
    PUT_CHAIN = 'PCHN'
    TRANSACTION = 'NTRS'
    BLOCK =  'NBLK'

    @staticmethod
    def len():
        return 4
