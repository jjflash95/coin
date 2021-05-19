from load_external import load_external
load_external()

from keys.keys import PrivateKey, PublicKey
from transaction import Transaction
from block import Block
from dotenv import load_dotenv
import os


skstr = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAthlK8aP9jv8n4qpeMwYa2qU0DTC3/YSyISFFPTcnVpsFwyUx
JiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pKpTn6PwI1nnz8Nl7Kv75f9c7RjnfP
f1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJI92OM8Thyt6JWYJZBh627+cwH11u
ZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWPQpS4Dafjj2+vSVFYCBdbiVJWlbzQ
KLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+yQtgdzCXUrTRYqpu7stLiJ11KZ4ne
W43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11kBQIDAQABAoIBAGzdOhy0OYYfrKyp
xZ8jazKDyVaJZbW+eu+rgEVUj8QK8ar0tSloq5TELxByocXne+g1M+I/iXJEDS7d
uZQqfO3Cd4TrwTp65h1rFjMDkULW3hkaL4ahcDDRE014D5wy5rpOo4V+oNXXaBKW
l487RTeX4Me6UHKEEADfGHG8MwnAXcj5QiWVmdqTysnSHCwL7rKhRZh5zLN3Ks4v
c2m9z0bI7lWfdy6z2eUDHEP1ketEtChCNMgcWSLHvQTreqNxTdPpwygkOTaCyIyY
kvi915z8K0xqoteSwxz1FB3FZQFQOY/4GSy3ofrOkmg1xW3u+WotZLIS+rddIuNE
ZwbjDxECgYEA6rnzOqmXvBHo8VcanDBSQB8HPa+oQc5l8tEEruX1DS0VcVDO6zOy
tdSgPzyb30z16j8u3seBvkpRBPCgAO4okJiIfCweRarCxYGZzPP+WnVr1w1wB61r
W8ENtSir7UwXEWCxnqYKjMSQJGhW59h3Ac2S0Wn3dghXxNLDTGOQwbMCgYEAxppL
NfUl0j8BfJ10WG/FhhMGf7jWk8ZFsyBmfMY5SiZGZcUzAK522SV3uHA0R3ZQJKQw
PUNRvtL+1AvXSZBAcytaWgvkViegS7fMmpQzsqHHEfkVuVSjNEUODseqes+VZTiY
rd20YWagDHnP+6n96FuMF5rj35+Ctd20Bo52N2cCgYEAmb8pCWCyiba1fPdP78Ra
67MnPAmFzWzTLEQqrCDl7TZ9mBaVIkxfn2hhempJsu8nGMNAAR5u5mSpQvIV6+YT
Xfr7U1JWlc1u/I2SX0Pmc/v7ogYkPnMiIhyGzQWR78HqTjCmx0L9IA1UWPSbEAui
j+TGaTLeq0p1qu9eiveghq8CgYBI0sTnWSfwKxhBeH7z+rAkFI/af413DEn8f9H0
yL6zGMvRf3jPNCnyP9HheItC9Pg4J1hk7m1oGnhEir77g4COeoQb5qZojQkzGodU
2ykFxFp5latIlOdvQC8CbmZtt/Zg8lrRzizZVkczq+r+rfujmwYIlcwe8J9+Tng3
uz9P2wKBgE4sRtn4p8B0jdO9TLtmod7Bym85fdoTZNYoNsSGxCfplKESPBU6bFmF
IBVVmPvmBUyssOmHk58l6yXpRhM6JUovOB10Bl1RgFeTFuvI405OnF9cvR2uc24S
ErA7uy0xyE8O0Pz8O9D7r3hJVhn640XS72ViKKACaLQnlSV9n3Q2
-----END RSA PRIVATE KEY-----"""

pkstr = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlK8aP9jv8n4qpeMwYa
2qU0DTC3/YSyISFFPTcnVpsFwyUxJiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pK
pTn6PwI1nnz8Nl7Kv75f9c7RjnfPf1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJ
I92OM8Thyt6JWYJZBh627+cwH11uZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWP
QpS4Dafjj2+vSVFYCBdbiVJWlbzQKLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+y
QtgdzCXUrTRYqpu7stLiJ11KZ4neW43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11k
BQIDAQAB
-----END PUBLIC KEY-----"""


load_dotenv()

print(os.getenv('KEYS_PATH'))
pk = PublicKey(path=os.getenv('KEYS_PATH'))
sk = PrivateKey(path=os.getenv('KEYS_PATH'))

pk2 = PublicKey(key=pkstr)
sk2 = PrivateKey(key=skstr)
# print(sk.id())

# print(pk, sk)
# print(pk2,sk2)
print(pk == pk2 and sk == sk2)