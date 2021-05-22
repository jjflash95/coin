
import inspect
import os
import sys


def load_external():
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir) 

load_external()

from dotenv import load_dotenv

load_dotenv()

from encryption.block import Block
from encryption.blockchain import BlockChain
from encryption.generate import coinbase, send
from encryption.keys.keys import PrivateKey, PublicKey
from encryption.transaction import Transaction
from storage.storage import Storage

def getkey(ktype=''):
    if ktype == 'secret': return PrivateKey(os.getenv('KEYS_PATH'))
    elif ktype == 'public': return PublicKey(os.getenv('KEYS_PATH'))

    return PrivateKey(os.getenv('KEYS_PATH')), PublicKey(os.getenv('KEYS_PATH'))


def recid():
    # random recipient id (publickey)
    return """MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2\
    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46\
    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW\
    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4\
    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6\
    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe\
    Dl4\nEwIDAQAB"""
