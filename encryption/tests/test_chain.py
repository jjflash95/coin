from load_external import load_external
load_external()

import os
from dotenv import load_dotenv

from generate import send, reward
from transaction import Transaction
from block import Block
from blockchain import BlockChain
from block import Block
from keys.keys import PrivateKey, PublicKey

recid = """MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46lsInRC\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvWZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU40XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDeDl4\nEwIDAQAB"""

transaction = r"""
{"data": {"amount": 0.33, "id": "62c2c047a239f8fe8c3d819c212ae736bf1deaaea87e82ab0ebcc122bd622187", 
"recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46lsInRC\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvWZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU40XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDeDl4\nEwIDAQAB", 
"sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlK8aP9jv8n4qpeMwYa\n2qU0DTC3/YSyISFFPTcnVpsFwyUxJiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pK\npTn6PwI1nnz8Nl7Kv75f9c7RjnfPf1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJ\nI92OM8Thyt6JWYJZBh627+cwH11uZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWP\nQpS4Dafjj2+vSVFYCBdbiVJWlbzQKLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+y\nQtgdzCXUrTRYqpu7stLiJ11KZ4neW43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11k\nBQIDAQAB"},
"signature": "RUmFLuWBgTM7DW7xmuqTNJFgJ/jj4jPfKxGkkY+GifsquRzIcIQffvxu6IJGb/EWaJV3vCqa4oDYf10DnzIz33gLQfVyIMqLzBQOJ20OG4Qxl2XffiH5wKFfcsmfhLRWxOiANxOdePafXsAy5ko1LNb0JiH8K/qrGT0sYMh+AIXHLZj8n2GOT8tTV6aiAVsrhrCwxGmVP1bdXOYkovTPtZ8HmNuDRVaMO6nOIahSuguiynxsr3JabMepjt5sKvwOe3DMEqa3H0pMOHb2kAe1fGuEsYnPIcg3Atc+qjrVDQ9Llt3Dd2dx1vFBMq0DEvgDljOGeCoaI2r1xoWotU3l/Q=="}"""


def blockgen(last_hash, yea=False):
    block = Block(reward(pk), last_hash)
    for t in [send(sk, pk, recid, .53), send(sk, pk, recid, .33)]:
        block.add(t)

    if yea:
        fraud = Transaction.from_json(transaction)
        # block.add(fraud)
        print('adding fraudulent transaction {}'.format(fraud.get_id()))
    return block.calculate_hash(challenge)    


def genesis():
    block = Block(reward(pk), 0)
    return block.calculate_hash(challenge)


load_dotenv()
challenge = 4

pk = PublicKey(path=os.getenv('KEYS_PATH'))
sk = PrivateKey(path=os.getenv('KEYS_PATH'))

bc = BlockChain([genesis()])

for i in range(2):
    newblock = blockgen(bc.get_last_hash(), i % 2)
    bc.add_block(newblock)

bc.validate_chain()
print(bc.to_json())
