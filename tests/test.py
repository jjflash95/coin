import os
from re import T

from dotenv import load_dotenv

from block import Block
from keys.keys import PrivateKey, PublicKey
from transaction import Transaction


load_dotenv()
print(os.getenv('KEYS_PATH'))
pk = PublicKey(path=os.getenv('KEYS_PATH'))
sk = PrivateKey(path=os.getenv('KEYS_PATH'))
# print(sk.id())


t = Transaction(sk, pk, 2, .14)

b = Block()
b.add(t)
b.add(Transaction(sk, pk, 2, .14))
b.add(Transaction(sk, pk, 324231, .142354))
b.add(Transaction(sk, pk, 4324246662, 1))
b.add(Transaction(sk, pk, 6564324232, 5))
# b.add(Transaction(sk, pk, 22233, 23))


b.calculate_hash(3)
print(b.to_json())
print(b.validate())
# print(b.transactions(), b.hash(), b.proof_of_work())
# print(b.to_json())
# print(b.validate())

# print(b.timestamp())
