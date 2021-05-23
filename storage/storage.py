from storage.models.models import BlockModel
from storage.models.models import ChainModel
from encryption.transaction import Transaction, Coinbase
from encryption.block import Block
from encryption.blockchain import BlockChain
from storage.db.db import Database
from storage.utils.utils import *


HASHCOL = 'block_hash'
INDEXCOL = 'block_index'


class Storage:
    def __init__(self, onmemory=False):
        self.db = Database(onmemory)

    def loadquery(self, q):
        return self.db.loadquery(q)

    def addchain(self, chain: BlockChain):
        for block in chain.getblocks():
            self.addblock(block)

    def addblock(self, block: Block):
        blockindex = block.index
        blockhash = block.hash
        previous_hash = block.previous_hash
        meanwhile = block.meanwhile
        createtime = block.timestamp

        query = self.__addblock(
            blockindex=blockindex,
            blockhash=blockhash,
            previous_hash=previous_hash,
            meanwhile=meanwhile,
            createtime=createtime)
        
        self.db.execute(query)
        
        coinbase = block.coinbase
        self.addcoinbase(blockhash=blockhash,
            coinbase=coinbase)
    
        transactions = block.transactions
        for transaction in transactions.all():
            self.addtransaction(blockhash=blockhash,
                transaction=transaction)


    def addcoinbase(self, blockhash, coinbase: Coinbase):
        coinbaseid = coinbase.get_id()
        recipient_id = coinbase.recipient_id
        query = self.__addcoinbase(blockhash=blockhash,
                                coinbaseid=coinbaseid,
                                recipient_id=recipient_id,
                                amount=coinbase.amount)

        self.db.execute(query)

    def addtransaction(self, blockhash, transaction: Transaction):
        transactionid = transaction.get_id()
        sender_id = transaction.sender_id
        recipient_id = transaction.recipient_id
        amount = transaction.amount
        signature = transaction.signature
        query = self.__addtransaction(transactionid=transactionid,
                                blockhash=blockhash,
                                sender_id=sender_id,
                                recipient_id=recipient_id,
                                amount=amount,
                                signature=signature)

        self.db.execute(query)

    def __addcoinbase(self, blockhash, coinbaseid, recipient_id, amount):
        query = """
        INSERT INTO `Coinbase` (id, blockhash, recipient_id, amount)
        VALUES ({}, {}, {}, {})
        """.format(addquotes(coinbaseid), addquotes(blockhash), addquotes(recipient_id), amount)
        return query

    def __addtransaction(self, transactionid, blockhash, sender_id, recipient_id, amount, signature):
        query = """
        INSERT INTO `Transaction` (id, blockhash, sender_id, recipient_id, amount, signature)
        VALUES ({}, {}, {}, {}, {}, {})
        """.format(addquotes(transactionid),
            addquotes(blockhash),
            addquotes(sender_id),
            addquotes(recipient_id),
            amount,
            addquotes(signature))

        return query

    def __addblock(self, blockindex, blockhash, previous_hash,  meanwhile, createtime):
        query = """
        INSERT INTO `Block` (bindex, bhash, previous_hash, meanwhile, createtime)
        VALUES ({}, {}, {}, {}, {})
        """.format(blockindex, addquotes(blockhash), addquotes(previous_hash), addquotes(meanwhile), createtime)
        return query
    
    def getblock(self, blockhash, buildcascade=False):
        query = """
        SELECT (bhash, previous_hash, meanwhile, createtime) FROM `Block`
        WHERE bash = {}
        """.format(addquotes(blockhash))

        self.db.execute(query)
        block = self.db.fetchall()

        if not block: return       
        if not buildcascade: return block[0]

        query = """
        SELECT (id, blockhash, recipient_id, amount) FROM `Coinbase`
        WHERE blockhash = {}
        """.format(addquotes(blockhash))

        self.db.execute(query)
        coinbase = self.db.fetchall()

        if not coinbase:
            return

        query = """
        SELECT (id, blockhash, sender_id, recipient_id, amount, signature)
        FROM `Transaction`
        WHERE blockhash = {}
        """.format(addquotes(blockhash))

        self.db.execute(query)
        transactions = self.db.fetchall()

        return block[0], coinbase[0], list(transactions)

    def __getchain(self, buildcascade=True):
        """
        IF NOT BUILDCASCADE, JUST RETURNS THE LONGEST ROUTE
        OF HASH => PREV_HASH PAIRS FOR EVERY BLOCK ON CHAIN
        AND IGNORES TRANSACTIONS AND COINBASE
        """
        query = self.loadquery('get_chain')
        if buildcascade:
            query = """
                SELECT b.bhash as block_hash, b.bindex as block_index,
                b.previous_hash as block_previous_hash, b.meanwhile as block_meanwhile,
                createtime as block_createtime, c.recipient_id as cbase_recipient_id,
                c.amount as cbase_amount, c.id as cbase_id, t.id as transaction_id,
                t.sender_id as transaction_sender_id, t.recipient_id as transaction_recipient_id,
                t.amount as transaction_amount, t.signature as transaction_signature
            FROM ({}) b
            LEFT JOIN `Transaction` t ON b.bhash = t.blockhash
            LEFT JOIN `Coinbase` c ON b.bhash = c.blockhash
            ORDER BY b.bindex, b.bhash, t.id
            """.format(query)

        self.db.execute(query)
        return self.db.fetchall()

    def getchain(self, buildcascade=True):
        blocks = self.__getchain(buildcascade)
        return blocks

    def commit(self):
        self.db.conn.commit()