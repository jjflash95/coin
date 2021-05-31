
import inspect
import os
import sys


def load_external():
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir) 

load_external()
from config import buildconfig

CONFIG = buildconfig()

KEYS_PATH = CONFIG['keys']['path']
DB_PATH = CONFIG['db']['path']

SERVERPORT = CONFIG['p2p']['serverport']
MAXPEERS = CONFIG['p2p']['maxpeers']
BUILDFROM = CONFIG['p2p']['buildfrom']
GUID = CONFIG['p2p']['guid']

from encryption.block import Block
from encryption.blockchain import BlockChain
from encryption.generate import coinbase, send
from encryption.keys.keys import PrivateKey, PublicKey
from encryption.transaction import Transaction
from encryption.utils.exceptions import *
from localstorage import LocalStorage
from p2p.network.requests import MSGType
from p2p.peer import Peer
from storage.models.models import ChainModel
from storage.storage import Storage


def getkey(ktype=''):
    if ktype == 'secret': return PrivateKey(KEYS_PATH)
    elif ktype == 'public': return PublicKey(KEYS_PATH)

    return PrivateKey(KEYS_PATH), PublicKey(KEYS_PATH)


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

def validblockchain():
    return r"""
    [
        {
            "coinbase": {
            "amount": 10,
            "id": "b3bf85ff010a18e21b9bd38c6b3555f2d0df0eabd1d7967afe198d7458ccb5cd",
            "recipient_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE="
            },
            "hash": "00006fb9edb0af9d912930ea16d2984cd19281b271be8f89bbaee03cf3d77a8a",
            "index": 1,
            "meanwhile": "31775",
            "previous_hash": "0",
            "timestamp": 1622430518.601016,
            "transactions": []
        },
        {
            "coinbase": {
            "amount": 10,
            "id": "0824793cf95e57f067b8af624ede5e045b4c02e08f5f75d810d90e83ae7a8f84",
            "recipient_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE="
            },
            "hash": "0000b15f7eaf2ffeedf172cd72183ce33bcb7f7eb6e9bac4cf321bbce184b5e7",
            "index": 2,
            "meanwhile": "13535",
            "previous_hash": "00006fb9edb0af9d912930ea16d2984cd19281b271be8f89bbaee03cf3d77a8a",
            "timestamp": 1622430518.799484,
            "transactions": [
            {
                "amount": 0.410448,
                "id": "0c5f44222358d138acd0dcc018cc2c1705fad44910ca74484850727e3316297a",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "a8vesNz0PdZ3KVceQElDLopuvvJfeXGjKsT4yDCLA7auwFvFF9Hsy8Nuugxf4yXE6otMpwD6zYTaUPWWgwGpD4Srm+dp1XmvlXMhv55IMsxpurUwJGxC9lON7rlLsqot7Cj/ELJECzIS9qXQRi+fv7bLn8osbkU+586NLkB5vv2mwZ9Ezt8lSxllt6jsXc6MiY7jEWeQnTakYcXwGe6MkOIWq4nU33wYZLKpw28Gr83ILmfQSJ0WlmmsXcHTa06za/scb9cBe9kHxEk99yl2KySL0CV8WIpCmgs6YNG3ilM8O0Z0wQhc3au22S5lFki7K27J+alG7P4wt1pWmKknOQ=="
            },
            {
                "amount": 0.845454,
                "id": "193099c468e059c964d6bd0ea252a32fd1df878c1eec9b9b8d8dba6cfe73dd9c",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "LaLHHbiX+Z+1Redgm0aLKtkBZzT2L7vIP0X0jd+Y0fkk3R9Gvrw3LjVJ9QrogAhLUSjnoxY4VCrcMyQmvR5Mqbfk2Tsf8bJUeK1tLqzynnFs/OloaG3mF2HI0zUnKyckZHvZ9l8HFcxZ72Gxr4IaaoRr9O8Q6AUWWrh+Etjo0NFbk78thukXJQNQ1+L+ttl1gAZPucRcgtx2KZ1aQ7OVyFgpF89d7fW86H5yJKW5uusYsfT23jJs0jnw5V8LVtJ0p5iV5pJUcw5BfwmeZxCVSl30PgsHbI3yo8UTKH8fANiywsMmQ1U1vmsJDlotdI9iscyP4k9PCN3Y43i2/MAvhQ=="
            },
            {
                "amount": 0.435948,
                "id": "ebd9beccc954aa7662babc26fda8761e5b19b453055c0a9b5dc520f8aca898f1",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "SORWKrlqYCziXeJf86K3A7NazkghA7jmu+EeGky41bxd6BfUfyKqDOogW1kblmumVKvcdKAW8tGqJoEb7RLPUT3OhW77MBDtIetDXEyMkSWdtxbvX8ObfVtW1lYQDhrkpwSyS+avP89UpgsrNwvjqpBelQsbt2RLjd5KVmbPBWL5JnzcYsQjEL+13rD82BpsGHXIEgzo4pGgKQ95V3aq/sijKCmC6rSX0L5dZLKIxrL2W+Wax7HUqX1WelgWLSNtIfxd4GJfbWEKzIxKuBeRhPjlQor9vrJlQQ/wh0Z1vshOgV2DL3M1dCF6f5DgsN1m4D3U6QMEDrwFB+XKVpeOdA=="
            }
            ]
        },
        {
            "coinbase": {
            "amount": 10,
            "id": "0e37e82cc739d8b9087dbf1eeb1ecf14cc863452df12bb43956a16f3f74c4a12",
            "recipient_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE="
            },
            "hash": "00009ed45f0c48d64d6491db1930280036865cedb376258bfd76027bdd59147f",
            "index": 3,
            "meanwhile": "99618",
            "previous_hash": "0000b15f7eaf2ffeedf172cd72183ce33bcb7f7eb6e9bac4cf321bbce184b5e7",
            "timestamp": 1622430519.164507,
            "transactions": [
            {
                "amount": 0.154056,
                "id": "4a133b3bc04dae2c995a33cc3c1e3ae04336367ba8d5835f301ad9dbc4a5c8c6",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "YAVPrcnLt/HFproN3FCS2hwy/hRKOU7lqxsuRj1hySmCS47w577oRNGmgo/0fecK1xDKDdJ2TshcHDppaOCX5JjQqTP+Hnjj1wt1FWTDNW7l9eDCw6E/jo/ro9w7CGzSsby8C5FoZ4qBHXEmpBZpbXWx7NnnKe8w8lkU7oA0S3qEhw38oC4R9uohelTbBco896EZOUDHiTLuY6TjMt2CclRmjoKYcXY6J7+McuBDi9mxug1cg0p016VKtPluACE9kAfC1ySufqQ4S0S/s8m3jjBgDIlNtlghZKpF3YQch/JXekYXrUePlKEuEU3dZ0wMKzUANJFGCIidpkxcuuYpTg=="
            },
            {
                "amount": 0.13637,
                "id": "be9233effdbdcf15c9e0039932181a1c56fee5451a052911353277f3a2790be9",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "XkGxHhdfRWwEQ9VSEL0lXPHQPJUqC/60etmcdPeRdiGRoZBSZACKILQZgSnXXA4/f23LV8VGS1XzcNulnAkEAtZ9nWH8IxBD3ShS52YelZWW+U5X1i3OgpGSobgYbcHkj1pNKGAM9vfVi6033r/SfN1eNWBHKszDZ/qKspEjjo4Vy2E2VdhVbPE8cNLEQS8PxhvJ7Lpk3/7XNajaxkDoAGWaVfW22Uj+EWw/DfVgT7EydOKfyQKR9bzPZbxBqmF+zS6wNWI/e+6B26w16cRnL+OIzH7d4HaImdSL3XA1dNstlpkE4jY5y9busUFcjAyxJNpBRwxC0xvPi8TiCQ57Tw=="
            },
            {
                "amount": 0.994917,
                "id": "d34d644374fcee91e1961eecd7fc90f1970ea80008ab810b96ff212ef15ea3f8",
                "recipient_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzv3SLBQLCrHR2    XeibAJK\nrno7f5NL2H57kmMOWf0Xebrx2kGyEaJK5Sq54bGWNsmbJLAMb3bl14Ml46    lsInRC\\nBv50EG+nk2DO5+B+O7gYmJUl7m3cgk6yKfsblnu8C0+m3+5myihH2prFvW    ZM8GhT\nLrOdgcQF1vHhmXj2d1zIgC5dkVZRLBceO2mRePAaYAOPrxnOGOVbU6IQGU4    0XXl4\nc6tqhocTJYk9hc/96pDh8gsclzE308Ibov8TOW0KwWc1hq7CMGkDDIW2gOP6    Qoa2\n4P5lOOlj33jIFqzigSkDsTdogFCCQy7nDJ+yJvrq5RlAxfacxz0JWIp4nbqDe    Dl4\nEwIDAQAB",
                "sender_id": "MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQB8PlY2frap+MmbYEnWJb9b\nMgpXFLsGm/3bmwAHIDPSh3r6d4ioorA5ONDJ+ftTqphE+aG5yeLA00bGiAoW9X7a\nysGr09Rsj/i368dZBaIHw1eEPT3hktBVQYWuvyJdFJ8muFd0SAWnhOaxAB1V3phu\n6Yew8bDXga6XO+4xqArwMMbOlmXw0sp/qu8dNzovNnutKYEYRSkSW/8mj46CnpbD\nLBjlLMramTkXHeb9V1SanMvzrXoQoyLKvUS7hLj3gpidx3b9voPV+KsVXddBuBer\neDncJfZFwBW+d8nx8xYk5hpF3QDLEryHE4LOoXDeQDhuRggALqSPgRp/RM5lIl0x\nAgMBAAE=",
                "signature": "Y9+qPtbTA9lMlx2GErqqRJirUFK+dM4vuu0OOlndjQnCK98Vb8OYTvm/CgnUccDKAcCHapPKR7WB3m+sOSaMxswg39gvavvKu7QrvLTcO3cuvOfAXrbJ7FEUrfsCuMV4+h9Rg4+2CFHNR8/mMhh9Re40IiaklAVBJoCDsUyMPXwNSCXhHyGSePGUm8toDYvAruEh7j8pWJIpODB+4DNix7z3DTYXWOGbcare1tyTg7rvETQPXxCf0gmUh5fgyx0405nwzsFKeSXgN+jJJJtH+5/HT+qB9c4MG6PGsLCK5QLUW5cKsAMyyEMcDcDRIzV4/5ycNjujMIyWXUTFlsENWA=="
            }
            ]
        }
    ]    
    """