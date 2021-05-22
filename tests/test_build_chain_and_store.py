from load_external import load_external
load_external()
import unittest

import os
from dotenv import load_dotenv

from encryption.generate import send, coinbase
from encryption.block import Block
from encryption.blockchain import BlockChain
from encryption.block import Block
from encryption.keys.keys import PrivateKey, PublicKey

from storage.storage import Storage

recid = """MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46lsInRC\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvWZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU40XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDeDl4\nEwIDAQAB"""

transaction = r"""
{"data": {"amount": 0.33, "id": "62c2c047a239f8fe8c3d819c212ae736bf1deaaea87e82ab0ebcc122bd622187", 
"recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46lsInRC\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvWZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU40XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDeDl4\nEwIDAQAB", 
"sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlK8aP9jv8n4qpeMwYa\n2qU0DTC3/YSyISFFPTcnVpsFwyUxJiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pK\npTn6PwI1nnz8Nl7Kv75f9c7RjnfPf1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJ\nI92OM8Thyt6JWYJZBh627+cwH11uZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWP\nQpS4Dafjj2+vSVFYCBdbiVJWlbzQKLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+y\nQtgdzCXUrTRYqpu7stLiJ11KZ4neW43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11k\nBQIDAQAB"},
"signature": "RUmFLuWBgTM7DW7xmuqTNJFgJ/jj4jPfKxGkkY+GifsquRzIcIQffvxu6IJGb/EWaJV3vCqa4oDYf10DnzIz33gLQfVyIMqLzBQOJ20OG4Qxl2XffiH5wKFfcsmfhLRWxOiANxOdePafXsAy5ko1LNb0JiH8K/qrGT0sYMh+AIXHLZj8n2GOT8tTV6aiAVsrhrCwxGmVP1bdXOYkovTPtZ8HmNuDRVaMO6nOIahSuguiynxsr3JabMepjt5sKvwOe3DMEqa3H0pMOHb2kAe1fGuEsYnPIcg3Atc+qjrVDQ9Llt3Dd2dx1vFBMq0DEvgDljOGeCoaI2r1xoWotU3l/Q=="}"""


def blockgen(last_hash, last_index):
    block = Block(coinbase(pk), last_hash, last_index)
    for t in [send(sk, pk, recid, .53), send(sk, pk, recid, .33)]:
        block.add(t)


    return block.calculate_hash(challenge)    


def genesis():
    block = Block(coinbase(pk))
    return block.calculate_hash(challenge)


load_dotenv()
# challenge = 3
# print(os.getenv('KEYS_PATH'))
# pk = PublicKey(path=os.getenv('KEYS_PATH'))
# sk = PrivateKey(path=os.getenv('KEYS_PATH'))

# bc = BlockChain([genesis()])

# for i in range(6):
#     newblock = blockgen(bc.get_last_hash(), bc.get_last_index())
#     bc.add_block(newblock)

# bc.validate_chain()

s = Storage(mem=True)

# for block in bc.get_blocks():
#     s.addblock(block)

# s.commit()
# for block in bc.get_blocks():
#     s.addblock(block)

# s.commit()

import json
class TestString(unittest.TestCase):
    def test1(self):
        print(json.dumps(s.getblocks()))
        self.assertEqual('foo', 'foo')

if __name__  == '__main__':
    unittest.main()