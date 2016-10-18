'''
    @author: Jhesed Tacadena
    @description:
        - contains function(s) for interacting with
        dragonpay api
'''

from . import dragonpay_config as DC
import xml.etree.ElementTree as ET
from hashlib import sha1
import string
from random import choice
from time import time
from models.dragonpay import Dragonpay
import features.logging as sms_api_logger
        
DRAGONPAY_TXN_PREFIX = 'CHKID_%s'


def get_dragonpay_token(account_id, checkout_id, email, amount, param1=None):
    '''
        @description:
            - abstracts dragonpay API implementation
            - uses dragonpay util to return dragon pay
            token id
    '''
    
    # logger
    scart_logger = sms_api_logger.SCartLogger()
    
    # generates a unique transaction id
    txn_id = DRAGONPAY_TXN_PREFIX %str(checkout_id) 
    description = 'CHIKKA API'
    
    scart_logger.info('dragon pay API soap call', {
        'user_id': account_id, 'txn_id': txn_id, 
        'amount': amount, 'email': email})
     
    try:
        return get_token_via_soap(txn_id=txn_id,
            amount=amount, email=email, description=description,
            param1=param1)[0]

    except Exception, e:
        scart_logger.error('dragonpay error', {
        'user_id': account_id, 'txn_id': txn_id, 
        'amount': amount, 'email': email,
        'error': str(e)})
        raise Exception('get dragonpay token failed')
   

def save_dragonpay_data(checkout_id):
    '''
        @description:
            - saves dragonpay data
            - returns the generated ctoken_id
            if data was successfully saved in DB
            to be able to pass to dragonpay
            soap call in handler(s)
    '''
    txn_id = DRAGONPAY_TXN_PREFIX %checkout_id
    ctoken_id = __generate_unique_ctoken()
    
    result = Dragonpay.save(txn_id=txn_id, ctoken_id=ctoken_id)
    return ctoken_id if result else False
    
    
def __generate_unique_ctoken(size=4):
    '''
        @description:
            - generates a unique chikka
            token that will be used
            for authentication later on
    '''
    chars = string.ascii_uppercase + string.digits
    token = '%s' %(time())
    random_hash = ''.join(choice(chars) for i in range(size))
    return ('%s_%s' %(token, random_hash))
    
    
"""    
def save_dragonpay_credentials(checkout_id, amount, email):
    '''
        @description:
            - save credentials taken from dragonpay
    '''
    
    hash = compute_sha1_digest(checkout_id, amount, email)
    return hash
"""


def get_token_via_soap(txn_id, amount, email, param1=None, 
    param2=None, description=None, ccy='PHP'):
    '''
        @description:
            - obtains token id from dragon api
            using soap call which will be used for
            identifying the user in dragon api's payment page.
        @param txn_id:
            - unique transaction id
        @param amount:
            - total amount purchased by user
        @param email:
            - email of user
        @param param1 param2:
            - optional parameters to be returned to the postback url
        @param description:
            - description of transaction
        @param ccy
            - currency of the transaction
    '''    
    scart_logger = sms_api_logger.SCartLogger()
    scart_logger.info("get token via soap", {"email":email})
        
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
  <GetTxnToken xmlns="%s">
    <merchantId>%s</merchantId>
    <secretKey>%s</secretKey>
    <password>%s</password>
    <txnId>%s</txnId>
    <merchantTxnId>%s</merchantTxnId>
    <amount>%.2f</amount>
    <ccy>%s</ccy>
    <description>%s</description>
    <email>%s</email>
    <param1>%s</param1>
  </GetTxnToken>
</soap:Body>
</soap:Envelope> 
""" %(DC['api_url'], DC['merchant_id'], DC['secret_key'],
    DC['secret_key'], txn_id, txn_id,
    amount, ccy, description, email, param1)
    
    scart_logger.info("soap body", {"body":repr(body)})
    headers = {
        'Host': DC['host'],
        'Content-Type': 'text/xml; charset=utf-8',
        'Content-Length': "%d" % len(body),
        'SOAPAction': DC['api_get_token_url']
    }

    scart_logger.info("using dragon pay", {"host":Dragonpay.http_conn.host, "uri":DC['uri'] })

    try:
        http_response = Dragonpay.http_conn.post(DC['uri'], body=body, headers=headers).read()
        response = __parse_soap_response(http_response)
    except Exception, e:
        import traceback
        print traceback.format_exc()
        return None
        
    # there should be a response in the form of a non-empty list        
    if not response:
        raise Exception('could not get token from Dragonpay. http response: %s'% http_response)
    # return response.read()
    scart_logger.info("response", {"response": repr(response) })
    return response
    
def dpsoap_send_billing_info(merchant_txn, first_name, last_name, address1, 
    address2, city, state, country, zipcode, telno, email):
    '''
        @description:
            - sends billing info to dragonpay
            - currently not being used
    '''
    
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
        response = Dragonpay.http_conn.post(uri, body=body, headers=headers)
    except Exception, e:
        print e
        return None
    return response.read()
    
def __parse_soap_response(xml_string):  
    '''
        @description:
            - extracts the data from soap xml response
        @returns list
    '''
    raw_list = []    
    try :
        element = ET.fromstring(xml_string)
        response = element.getchildren()[0].getchildren()[0].getchildren()
        for r_element in response :
            raw_list.append(r_element.text)   
    except :
        raw_list = []
     
    return raw_list
    
    
def compute_sha1_digest(checkout_id, amount,
    email, currency='PHP'):
    '''
        @deprecated
        @description:
            - computes the SHA1 equivalent based from
            the dragonpay parameters passed
            - txn_id is CHKID_<checkout_id>
    '''    
    
    txn_id = 'CHKID_%s' %checkout_id
    description = 'CHIKKA API'
    message = '%s:%s:#%.2f:%s:%s:%s:%s' %(DC['merchant_id'], checkout_id,
        amount, currency, description, email, DC['secret_key'])
    
    return hash
        
def validate_dragonpay_digest(txn_id, refno,
    status, message, dragonpay_digest, ctoken_id):
    '''
        @description:
            - validates dragonpay digest 
            based on returned dragonpay response
            - if computed hash is equal to 
            the passed @param dragonpay_digest,
            it is valid, else not
            - txn_id is CHKID_<checkout_id>
         
    '''
    
    # txn_id = 'CHKID_%s' %checkout_id
    description = 'CHIKKA API'
    msg = '%s:%s:%s:%s:%s' %(txn_id, refno,
        status, message, DC['secret_key'])
    
    hash = sha1(msg).hexdigest()
    
    print msg
    print hash
     
    if hash == dragonpay_digest:
        return True
    return False

def is_allowed_for_amount( amount ):
    
    is_allowed = False
    
    if float(amount) >= DC['min_amount_peso']:
        print 'amount is allowed', float(amount)
        is_allowed = True
    else:
        print 'not allowed'
        is_allowed = False
        
    
    return is_allowed