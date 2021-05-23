# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
from load_external import PublicKey, PrivateKey, getkey
from load_external import *
import os
import unittest


class TestKeys(unittest.TestCase):
    """
    THIS TESTS ARE SUPPOSED TO CHECK THAT KEY PAIRS WORK AS
    INTENDED, THAT SIGNING AND VERIFICATION IS CORRECTLY
    IMPLEMENTED AND LOADING A KEY FROM A STRING ASWELL AS AN 
    RSA-FORMATTED FILE WORK THE SAME WAY
    """


    def testLoadInvalidKey(self):
        with self.assertRaises(Exception) as context:
            PrivateKey.from_string('invalid string')
        
        self.assertTrue('Could not deserialize key data.' in str(context.exception))

    def testPrivateKeysEqualFromStringAndFromEnv(self):
        with open('{}/{}'.format(os.getenv('KEYS_PATH'), 'private_key.pem'), 'r') as k:
            text = k.read()
        textsecret = PrivateKey.from_string(text)
        pathsecret = getkey('secret')
        self.assertEqual(str(textsecret), str(pathsecret))

    def testPublicKeysEqualFromStringAndFromEnv(self):
        with open('{}/{}'.format(os.getenv('KEYS_PATH'), 'public_key.pem'), 'r') as k:
            text = k.read()
        textpublic = PublicKey.from_string(text)
        pathpublic = getkey('public')
        self.assertEqual(str(textpublic), str(pathpublic))

    def testValidSigningAndVerifyWithPair(self):
        secret, public = getkey()
        example = 'text to be signed'
        signature = secret.sign(example)
        verification = public.verify(example, signature)
        self.assertEqual(verification, True)

    def testInvalidSigningAndVerifyWithPair(self):
        secret, public = getkey()
        example = 'text to be signed'
        modified = 'modified text for signature'
        signature = secret.sign(example)
        verification = public.verify(modified, signature)
        self.assertEqual(verification, False)


if __name__ == '__main__':
    unittest.main()