

class Type():
    PEERGUID = 'GUID'
    ROUTING_TABLE = 'CPRT'
    PEERJOIN = 'JOIN'
    PEERQUIT = 'QUIT'

    REPLY = 'REPL'
    ERROR = 'ERRO'


    @staticmethod
    def len():
        return 4