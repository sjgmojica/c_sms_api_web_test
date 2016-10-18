'''
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        -encapsulates the text API calls
        in sending MT messages and MO replies
'''

from time import time
from urllib import urlencode
from urllib2 import Request, build_opener
from . import text_api_config

# to transfer to yaml
TEXT_PINCODE_URL = text_api_config['pincode_url']
TEXT_MT_URL = text_api_config['mt_url']
TEXT_MESSAGE = 'Hello. Your verification code is %s.  Please input it in your browser'

MESSAGE_ID = 'messageid%s'

# -------------------------
# --- SENDING SMS ---
# -------------------------

def send_trial_mt(suffix, phone, mt_message, client_id, secret_key):
    '''
        @description:
            - sends MT message for 
            account type TRIAL
    '''
    
    phone = '639%s' %str(phone[-9:])
    message_id = MESSAGE_ID %str(time()).replace('.', 'm')
    
    mt_message = mt_message.encode("utf-8") 
    
    BODY = {
        'message_id': message_id,
        'message_type': 'SEND',
        # 'encoding': 'SMS',
        'mobile_number': phone,
        'message': mt_message,
        'charge': 'FREE',
        'shortcode': '29290%s' %suffix
        # 'client_id': client_id,
        # 'secret_key': secret_key
    }
    
    print urlencode(BODY)
    request(url=TEXT_MT_URL, 
        http_method='POST', data=urlencode(BODY))
    return message_id


def send_generic_sms( phone, body ):
    
    message_id = __send_sms( phone=phone,  body=body )
    
    return message_id
    

def send_pincode(account_id, phone, pincode):
    # just to be sure that phone has correct format
    phone = '639%s' %str(phone[-9:])
    message_id = MESSAGE_ID %str(time()).replace('.', 'm')
    body = TEXT_MESSAGE % str(pincode)
    
    BODY = {
        'message_id': message_id,
        'receiver': phone,
        'body': body
    }
    
    request(url=TEXT_PINCODE_URL, 
        http_method='POST', data=urlencode(BODY))
    
    return message_id
        



def __send_sms( phone,  body, ):
    # just to be sure that phone has correct format

    #phone should be in 639XXXXXXXXX format
    phone = __filter_mobile( phone )

    message_id = MESSAGE_ID %str(time()).replace('.', 'm')

    BODY = {
        'message_id': message_id,
        'receiver': phone,
        'body': body
    }

    request(url=TEXT_PINCODE_URL, 
        http_method='POST', data=urlencode(BODY))


    return message_id


    
def request(url, http_method, data=None, headers=None):
    try:
        if headers:
            req = Request(url, data, headers)
        else:    
            req = Request(url, data)
        
        req.get_method = lambda: http_method
        can_opener = build_opener()
        response = can_opener.open(req).read()
        
        print '--------------'
        if headers:
            print headers
        print data
        print response
        print '--------------'
        
        return response

    except Exception, e:
        print e
    return False
    
"""
print '========================'
print send_pincode('53', '09066803224', 'ABNPQW')
print '========================'
"""

def __filter_mobile( mobile_filter ):
    '''
    code is transplanted from foregin module
    
    '''
    #check the format used
    # possible accepted formats
    #    09XXXXXXXXX
    #  +639XXXXXXXXX
    #     9XXXXXXXXX
    if mobile_filter and len(mobile_filter) <= 13  :

        # filter invalid characters in mobile filter
        # should only accept format 639XXXXXXXXX
        for mobile_char in mobile_filter :

            if mobile_char not in '+1234567890':
                mobile_filter=None
                raise Exception('invalid mobile filter') 
                
                break
        if len(mobile_filter) == 11 and mobile_filter[0:2] == '09':
            mobile_filter = '63%s' % mobile_filter[1:]
        elif len(mobile_filter) == 13 and mobile_filter[0:4] == '+639':
            mobile_filter = mobile_filter[1:]
        elif len(mobile_filter) == 12 and mobile_filter[0:3] == '639':
            #mobile_filter = mobile_filter
            pass
        elif len(mobile_filter) == 10 and mobile_filter[0:1] == '9':
            mobile_filter = '63%s' % mobile_filter[1:]
        else :
            mobile_filter=None
    else:
        mobile_filter = None    
    
    
    
    return mobile_filter