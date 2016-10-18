'''
    @author: Jhesed Tacadena
    @description: 
        handles functions used for
        MT messages
    @date: 2013-10 
'''

from models.account import Account
from models.verification import Verification
from utils.text_api import send_trial_mt
import features.logging as sms_api_logger

DEFAULT_MESSAGE = 'Welcome to Chikka API!'
SENT_TRIAL_MESSAGE = 'Sent via Chikka API - %s' # 22 chars long
MESSAGE_LEN = 118  # 160 - len(SENT_TRIAL_MESSAGE)

def get_testmin(account_id):
    '''
        returns testmin
    '''
    testmin = Account.get(account_id=account_id)
    if not testmin:
        return None
    return testmin.test_min

def get_mt_obj(account_id):
    mt_obj = {}
    acct_obj = Account.get(account_id)
    if acct_obj:
        mt_obj['testmin'] = acct_obj.test_min
        mt_obj['suffix'] = acct_obj.suffix
        mt_obj['mo_reply'] = acct_obj.test_mo_reply[len(SENT_TRIAL_MESSAGE)-2:]
        mt_obj['client_id'] = acct_obj.client_id
        mt_obj['secret_key'] = acct_obj.secret_key
    
    return mt_obj
        
def send_mt_message(account_id, suffix, testmin, mt_message, client_id, secret_key):
    '''
        uses API to send MT message
        to user
    '''
    
    gen_logger = sms_api_logger.GeneralLogger() 
        
    if not mt_message:
        message_id = send_trial_mt(suffix, testmin, 
            SENT_TRIAL_MESSAGE % DEFAULT_MESSAGE,
            client_id, secret_key)
    elif len(mt_message) > MESSAGE_LEN:
        message_id = None
    else:
        message_id = send_trial_mt(suffix,
            testmin, SENT_TRIAL_MESSAGE % mt_message,
            client_id, secret_key)
        
    gen_logger.info('Hitting API to sending MT message', 
        {'account_id': account_id, 'mobile': testmin, 'suffix': suffix, 'message_id': message_id})
            
    Verification.set_message_sent_to_pending(
        testmin[-12:], message_id)
    
    return message_id
    
def set_message_sent_to_success(mobile, message_id):
    
    gen_logger = sms_api_logger.GeneralLogger()    
    try:
        return Verification.set_message_sent_to_success(
            mobile, message_id)
    except Exception, e:
        gen_logger.error('TEST MT sent status to SUCCESS', 
            {'mobile': mobile, 'message_id': message_id})
            
def get_message_sent_status(mobile, message_id):
    return Verification.get_message_sent_status(
        mobile, message_id)
