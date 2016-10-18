'''
    @author: Jhesed Tacadena
'''

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

host = "http://test.dragonpay.ph"
uri = "/DragonPayWebService/MerchantService.asmx"
merchant_id = 'CHIKKA'
secret_key = 'Zm@K7uP3q'

host_header = "test.dragonpay.ph"
api_url = "http://api.dragonpay.ph/"

# api defined urls
GetTxnToken_url = "%sGetTxnToken" %api_url
SendBillingInfo_url = "%sSendBillingInfo" %api_url


# ! TEST ONLY !
url = URL(host)
http_conn = HTTPClient.from_url(url, concurrency=10, ssl_options={'cert_reqs': 0 }) 


def dpsoap_get_token(txn_id, amount, email, postback1=None, 
    postback2=None, description=None, ccy='PHP'):
    
    # <param1>%s</param1>
    # <param2>%s</param2>
    
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
  <GetTxnToken xmlns="%s">
    <merchantId>%s</merchantId>
    <secretKey>%s</secretKey>
    <password>%s</password>
    <txnId>%s</txnId>
    <amount>%.2f</amount>
    <ccy>%s</ccy>
    <description>%s</description>
    <email>%s</email>
  </GetTxnToken>
</soap:Body>
</soap:Envelope> 
""" %(api_url, merchant_id, secret_key, secret_key, txn_id, 
    amount, ccy, description, email)

    print body
    
    headers = {
        'Host': host_header,
        'Content-Type': 'text/xml; charset=utf-8',
        'Content-Length': "%d" % len(body),
        'SOAPAction': GetTxnToken_url
    }
    
    print headers 
    
    try:
        response = http_conn.post(uri, body=body, headers=headers)
    except Exception, e:
        print e
        return None
        
    return response.read()

def dpsoap_send_billing_info(merchant_txn, first_name, last_name, address1, 
    address2, city, state, country, zipcode, telno, email):
    
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
  <SendBillingInfo xmlns="%s">
    <merchantId>%s</merchantId>
    <merchantTxnId>%s</merchantTxnId>
    <firstName>%s</firstName>
    <lastName>%s</lastName>
    <address1>%s</address1>
    <address2>%s</address2>
    <city>%s</city>
    <state>%s</state>
    <country>%s</country>
    <zipCode>%s</zipCode>
    <telNo>%s</telNo>
    <email>%s</email>
  </SendBillingInfo>
</soap:Body>
</soap:Envelope> 
""" %(api_url, merchant_id, merchant_txn, first_name, last_name, address1, 
    address2, city, state, country, zipcode, telno, email)

    print body
    
    headers = {
        'Host': host_header,
        'Content-Type': 'text/xml; charset=utf-8',
        'Content-Length': "%d" % len(body),
        'SOAPAction': SendBillingInfo_url
    }
  
    print headers
    
    try:
        response = http_conn.post(uri, body=body, headers=headers)
    except Exception, e:
        print e
        return None
    return response.read()
    
    
# ! TEST !

# get token    
txn_id = '1234'
amount = 1.00
email = 'test.com'
# postback1 = 'http://10.11.2.225:55566/test'
# postback2 = 'http://10.11.2.225:55566/test'
description = 'test'

# send billing info
first_name = 'first'
last_name = 'last'
address1 = 'my address 1'
address2 = 'my address 2'
city = 'mycity'
country = 'philippines'
state = 'philippines'
zipcode = '1234'
telno = '6511111'
email = 'test@test.com' 

# merchant_txn = dpsoap_get_token(txn_id, amount, email, postback1, postback2, description)
merchant_txn = dpsoap_get_token(txn_id, amount, email, description=description)
print merchant_txn

# merchant_txn = "3a42b51ff1531ab9a989ba703869a268" # ! TEST
# merchant_txn = "12345" # ! TEST

# print dpsoap_send_billing_info(merchant_txn, first_name, last_name, address1, 
    # address2, city, state, country, zipcode, telno, email)