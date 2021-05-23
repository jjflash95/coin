
from encryption.keys.keys import Signature
from encryption.transaction import Transaction, Coinbase
from encryption.block import Block
from encryption.blockchain import BlockChain
from storage.db.db import Database
from storage.utils.utils import *


class Storage:
    def __init__(self, onmemory=False):
        self.db = Database(onmemory)

    def loadquery(self, q):
        return self.db.loadquery(q)

    def addchain(self, chain: BlockChain):
        for block in chain.get_blocks():
            self.addblock(block)

    def addblock(self, block: Block):
        blockindex = block.index
        blockhash = block.hash
        previous_hash = block.previous_hash
        meanwhile = block.meanwhile
        createtime = block.timestamp()

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
    
    def getblock(self, blockhash, build=False):
        query = """
        SELECT (bhash, previous_hash, meanwhile, createtime) FROM `Block`
        WHERE bash = {}
        """.format(addquotes(blockhash))

        self.db.execute(query)
        block = self.db.fetchall()

        if not block: return       
        if not build: return block[0]

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

    def getblocks(self, build=False):
        query = self.loadquery('get_blocks')
        if build:
            query = """
            SELECT b.bhash, b.bindex, t.id,
            t.sender_id, t.recipient_id,
            t.amount, t.signature FROM `Transaction` t
            INNER JOIN ({}) b ON
            t.blockhash = b.bhash
            ORDER BY b.bhash
            """.format(query)

        self.db.execute(query)
        return list(self.db.fetchall())

    def commit(self):
        self.db.conn.commit()