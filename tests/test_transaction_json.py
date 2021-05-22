from load_external import load_external
load_external()

from transaction import Transaction


validt = r"""
 {"data": {"amount": 0.33, "id": "62c2c047a239f8fe8c3d819c212ae736bf1deaaea87e82ab0ebcc122bd622187", 
 "recipient_id": 2134, 
 "sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlK8aP9jv8n4qpeMwYa\n2qU0DTC3/YSyISFFPTcnVpsFwyUxJiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pK\npTn6PwI1nnz8Nl7Kv75f9c7RjnfPf1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJ\nI92OM8Thyt6JWYJZBh627+cwH11uZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWP\nQpS4Dafjj2+vSVFYCBdbiVJWlbzQKLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+y\nQtgdzCXUrTRYqpu7stLiJ11KZ4neW43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11k\nBQIDAQAB"},
  "signature": "RUmFLuWBgTM7DW7xmuqTNJFgJ/jj4jPfKxGkkY+GifsquRzIcIQffvxu6IJGb/EWaJV3vCqa4oDYf10DnzIz33gLQfVyIMqLzBQOJ20OG4Qxl2XffiH5wKFfcsmfhLRWxOiANxOdePafXsAy5ko1LNb0JiH8K/qrGT0sYMh+AIXHLZj8n2GOT8tTV6aiAVsrhrCwxGmVP1bdXOYkovTPtZ8HmNuDRVaMO6nOIahSuguiynxsr3JabMepjt5sKvwOe3DMEqa3H0pMOHb2kAe1fGuEsYnPIcg3Atc+qjrVDQ9Llt3Dd2dx1vFBMq0DEvgDljOGeCoaI2r1xoWotU3l/Q=="}"""

invalidt = r"""
 {"data": {"amount": 0.33, "id": "62c2c047a239f8fe8c3d819c212ae736bf1deaaea87e82ab0ebcc122bd622187", 
 "recipient_id": 2134, 
 "sender_id": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlK8aP9jv8n4qpeMwYa\n2qU0DTC3/YSyISFFPTcnVpsFwyUxJiuTJ2KVQ/2BZto+4XRba1ys7RZlD1xXM4pK\npTn6PwI1nnz8Nl7Kv75f9c7RjnfPf1BOvFe9FTfVRQp/4+m31wh7tCfROuAMytUJ\nI92OM8Thyt6JWYJZBh627+cwH11uZBcROzvZ9XqijAVx30FcCaUNcPEoeVbmUOWP\nQpS4Dafjj2+vSVFYCBdbiVJWlbzQKLub2DA/hWu1v3zpjxbQlf2MFG6c99vbFj+y\nQtgdzCXUrTRYqpu7stLiJ11KZ4neW43kH1OCIbBtCL63x0K1eclA+LDBT5N8u11k\nBQIDAQAB"},
  "signature": "2RUmFLuWBgTM7DW7xmuqTNJFgJ/jj4jPfKxGkkY+GifsquRzIcIQffvxu6IJGb/EWaJV3vCqa4oDYf10DnzIz33gLQfVyIMqLzBQOJ20OG4Qxl2XffiH5wKFfcsmfhLRWxOiANxOdePafXsAy5ko1LNb0JiH8K/qrGT0sYMh+AIXHLZj8n2GOT8tTV6aiAVsrhrCwxGmVP1bdXOYkovTPtZ8HmNuDRVaMO6nOIahSuguiynxsr3JabMepjt5sKvwOe3DMEqa3H0pMOHb2kAe1fGuEsYnPIcg3Atc+qjrVDQ9Llt3Dd2dx1vFBMq0DEvgDljOGeCoaI2r1xoWotU3l/Q=="}"""


validtr = Transaction.from_json(validt)
invalidtr = Transaction.from_json(invalidt)


assert validtr.validate() == True
print('asserted valid transaction validates: OK')
assert invalidtr.validate() == False
print('asserted invalid transaction doesn\'t validate: OK')
