from load_external import load_external; load_external()
from peer import Peer
import threading
import sys

# from network.peer import Peer
from network.connection import P2PConnection


host, port = sys.argv[1].split(':')

p = Peer(5, 5007)
t = threading.Thread(target=p.main)
t.start()
p.buildpeers(host, int(port), 5)




# p.QUEUE.put(('propagate', '{TRANSACTION: XDDD!!}'))

print('BUILT PEERS!!!', p.PEERS)

transaction = """
{"id": "1234", "t": "XD"}
"""

p.propagate(transaction)
p.getchain()


