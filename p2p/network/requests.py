

class MSGType():
    PEERGUID = 'GUID'
    ROUTING_TABLE = 'CPRT'
    PEERJOIN = 'JOIN'
    PEERQUIT = 'QUIT'

    REPLY = 'REPL'
    ERROR = 'ERRO'

    GET_CHAIN = 'GTCH'
    TRANSACTION = 'NTRS'

    @staticmethod
    def len():
        return 4
