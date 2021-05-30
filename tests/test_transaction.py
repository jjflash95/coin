# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from load_external import (
    Transaction, getkey, send, recid, validtransaction,
    invalidtransaction, InvalidKeyException, InvalidAmountException
)
from load_external import *
import unittest
import random
import threading


class TestTransactions(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK TRANSACTION MAKING WORKS
    AS INTENDED, LOADING FROM A JSON STRING, AS WELL AS BUILD
    A TRANSACTION BY ITS API SHOULD YIELD THE SAME RESULTS
    GIVEN THE SAME DATA AND SIGNATURE WHEN VALIDATING
    """

    def maketransaction(self, sk, pk, recipient_id, amount=None):
        if amount is None: amount = random.random()
        return send(sk, pk, recipient_id, amount)

    def testMakeValidTransactionViaJson(self):
        transaction = validtransaction()
        transaction = Transaction.from_json(transaction)
        self.assertTrue(transaction.validate(),
            'JSON VALID transaction.validate() is not True')

    def testMakeValidTransactionViaApi(self):
        sk, pk = getkey()
        transaction = send(sk, pk, recid(), 10)
        self.assertTrue(transaction.validate(),
            'API VALID transaction.validate() is not True')
    
    def testMakeInvalidTransactionViaJson(self):
        transaction = invalidtransaction()
        transaction = Transaction.from_json(transaction)
        self.assertFalse(transaction.validate(),
            'JSON INVALID transaction.validate() is not False')

    def testMakeInvalidTransactionViaApi(self):
        sk, pk = getkey()
        transaction = send(sk, pk, recid(), 10)
        # changing transaction amount from 10 to 0.1 after signing
        # should yield False on validate()
        transaction.amount = 0.1
        self.assertFalse(transaction.validate(),
            'API INVALID transaction.validate() is not False')

    def testMakeInvalidNegativeAmountViaApi(self):
        # technically the signature should yield false, but adding test anyway
        sk, pk = getkey()
        transaction = send(sk, pk, recid(), 1)
        transaction.amount = -1
        self.assertFalse(transaction.validate())
    
    def testMakeInvalidTransactionsWithParamsMissing(self):
        sk, pk = getkey()
        self.assertRaises(InvalidKeyException, send, sk, '', recid(), 1)
        self.assertRaises(InvalidKeyException, send, '', pk, recid(), 1)
        self.assertRaises(InvalidKeyException, send, pk, sk, '', 1)
        self.assertRaises(InvalidAmountException, send, sk, pk, recid(), -1)

    def testMakeTransactionViaApiAndLoadViaJsonCompare(self):
        sk, pk = getkey()
        t1 = send(sk, pk, recid(), 1)
        t2 = t1.to_json()
        self.assertTrue(t1 == t2)

        import copy
        t3 = copy.deepcopy(t1)
        self.assertTrue(t1 == t3)
        t3.amount = 3
        self.assertFalse(t1 == t3)


if __name__ == '__main__':
    unittest.main()

