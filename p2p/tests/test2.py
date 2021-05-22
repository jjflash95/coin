from load_external import load_external; load_external()
from peer import Peer


# from network.peer import Peer
from network.connection import P2PConnection


p = Peer(5, 5005)
p.buildpeers(*'192.168.43.164:5004'.split(':'), 5)
p.main()
print('BUILT PEERS!!!', p.PEERS)

