from epeer import ExtendedPeer

# from network.peer import Peer
from network.connection import P2PConnection


p = ExtendedPeer(5, 5005)
p.buildpeers(*'192.168.0.244:5004'.split(':'))
p.main()


