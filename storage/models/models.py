from encryption.block import Block
from encryption.blockchain import BlockChain
from encryption.keys.keys import Signature
from encryption.transaction import Coinbase, Signature, Transaction


class TransactionModel:

    @staticmethod
    def build(transaction):
        tid = transaction.get('transaction_id')
        sender_id = transaction.get('transaction_sender_id')
        recipient_id = transaction.get('transaction_recipient_id')
        amount = transaction.get('transaction_amount')
        signature = transaction.get('transaction_signature')

        if None in [tid, sender_id, recipient_id, amount, signature]:
            return False

        t = Transaction(tid, sender_id, recipient_id, amount, Signature(signature))

        if t.validate():
            return t


class BlockModel:
    
    @staticmethod
    def build(transactions):
        header = transactions[0]
        blockhash = header.get('block_hash')
        prevhash = header.get('block_previous_hash')
        meanwhile = header.get('block_meanwhile')
        lastindex = header.get('block_index') - 1
        timestamp = header.get('block_createtime')
        cbid = header.get('cbase_id')
        cbrecid = header.get('cbase_recipient_id')
        cbamount = header.get('cbase_amount')

        coinbase = Coinbase(id=cbid, recipient_id=cbrecid)
        block = Block(coinbase=coinbase,
            previous_hash=prevhash,
            last_index=lastindex,
            hash=blockhash,
            meanwhile=meanwhile,
            timestamp=timestamp)

        transactions = [TransactionModel.build(t) for t in transactions]
        transactions = list(filter(bool, transactions))
        
        block.add(transactions)
        return block


class ChainModel:
    """
    THIS ARRAY IS SUPPOSED TO BE SORTED (ORDERED) BY
    BLOCKINDEX, BLOCKHASH AND TRANSACTIONID
    """

    @staticmethod
    def build(records):
        blocks = []
        transactions = []
        lastindex = None

        for record in records:
            index = record.get('block_index')
            if index != lastindex and lastindex is not None:
                blocks.append(BlockModel.build(transactions))
                transactions = []
            lastindex = index
            transactions.append(record)
        blocks.append(BlockModel.build(transactions))
        blockchain = BlockChain(blocks)
        return blockchain