
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
from encryption.utils.exceptions import *
from storage.models.models import ChainModel

from p2p.peer import Peer

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


def validtransaction():
    return r"""
     {
        "amount": 0.386001,
        "id": "fe4451c6e0e35f4630a54ceb02d49c094b8c082a598a5c46778b6160735c962e",
        "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
        "sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAolWu/eCbApvOUHgRA7PR\nuFZ0Ny+y7AIe3CLtBEFcRCU0Y9gGbeSeqFAVCGaRr29IChRjXy06PJCFzmPRGBWP\nwNs1Mr1B46Uf/8fX8a8TNibAdgaMcuAS6AS46OItYFZBYtSjQ6c8tE/NpZd2OGM0\n0eK3XfnXpT62HFqvtmLJSjdCgyHlDNLRkDEOPCSmZPV+Ebz8Dwq4Ho6+QNLKCQpO\nuqV4yfz+gXOlyBxGkLPV029DuvgKWWLd3usxeDVnMCUA+yKyO7p1ShpNdXIO1u9E\nk9AaTbji/Miyar3Kpn/dOBL4bv9uDfx2CLTxV7+rUSley3mm7qrXI3gxpyYBkKgL\nvwIDAQAB",
        "signature": "O23/B0eM+khJzrOTx8luMY+o6+JgU7PAQH1+QWQAkn72/YQE1RLHX3XtKv38SrdP5r+9ym9LQxjcUbWZXIjY78h9ruBvv5ivUHDa8zUGz+aPoj265P9XCrBv6KfnBYXSI6WkFS35YN1roH+pOM+KSfoN/p3WoQEk2xKGSgeQfQQ+oM4bCWrvV7T8x2kVgLkXtRL9PXR3ASxoSF7AHAQ+AAn85gxONnAA2h6HvUGdZmr+3p4ftVPEl+x8phng3/wthwMAhULKLvr4aMHT8mqoK0Q5NDXOHKEuj+iZhe9TGENXWwULWTWvpNLPbd3j+mgSAkh5WFPE2ATc4rlZxRRImQ=="
      }
    """

def invalidtransaction():
    return r"""
     {
        "amount": 10.8041491378037088,
        "id": "0817eb256db9b66da022df0a949c0c28a86bd60a5714769567f32cb2c5fccf74",
        "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
        "sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAolWu/eCbApvOUHgRA7PR\nuFZ0Ny+y7AIe3CLtBEFcRCU0Y9gGbeSeqFAVCGaRr29IChRjXy06PJCFzmPRGBWP\nwNs1Mr1B46Uf/8fX8a8TNibAdgaMcuAS6AS46OItYFZBYtSjQ6c8tE/NpZd2OGM0\n0eK3XfnXpT62HFqvtmLJSjdCgyHlDNLRkDEOPCSmZPV+Ebz8Dwq4Ho6+QNLKCQpO\nuqV4yfz+gXOlyBxGkLPV029DuvgKWWLd3usxeDVnMCUA+yKyO7p1ShpNdXIO1u9E\nk9AaTbji/Miyar3Kpn/dOBL4bv9uDfx2CLTxV7+rUSley3mm7qrXI3gxpyYBkKgL\nvwIDAQAB",
        "signature": "BQrl/IPw47oWD8yW0BaiGZrFU+OlPniRmUUDuF8OYGIZdGQI12niIg35CjU1xMaPPSMwPEoVf8SHt0QtcukyTd8R9PHJmFZzD6Q1b7gdnBbQiFGqKLd+G11Jvsj8XZEAdAVTM0LrDoaYKgPJeQN1IDqgUIze/Vi7QExYFr0ZQqCRIaNdqm0a+LfLcWA6zIPLdmSawl54SC1ApFzZR83/Hx+QdJPPfcWZGF3+04OFKTlrVW7LuNZ8ESvv3t6UX7CWDU698cspvrHbSrEdevycSYhkU+YHjs8oLhoTirCoKMonBuQadV2OfSpj4/dte/fFqXFL967tgPnkSAwtEW8TQQ=="
      }
    """