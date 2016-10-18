'''
    @author: Jhesed Tacadena
    @description: 
        handles functions used for
        MO messages
    @date: 2013-10  
'''

from models.account import Account
import features.logging as sms_api_logger

DEFAULT_MESSAGE = 'Hello, this is a sample MT message'
SENT_TRIAL_MESSAGE = 'Sent via Chikka API - %s' # 22 chars long
MESSAGE_LEN = 118  # 160 - len(SENT_TRIAL_MESSAGE)

def get_mo_obj(account_id):
    '''
        returns the MO message
        saved in Account table
    '''
    mo_obj = {}
    acct_obj = Account.get(account_id)
    if acct_obj:
        mo_obj['message'] = acct_obj.test_mo_reply
        mo_obj['testmin'] = acct_obj.test_min
    
    return mo_obj
    
            
def save_mo_message(account_id, mo_message):
    '''
        saves MO message in
        Account table
    '''
    if len(mo_message) > MESSAGE_LEN:
        return None
        
    gen_logger = sms_api_logger.GeneralLogger()    
    gen_logger.info('testmin MO -- saving MO reply',
        {'account_id': account_id, 'mo_message': mo_message})
            
    return Account.update(account_id=account_id,
        test_mo_reply=(SENT_TRIAL_MESSAGE % mo_message))
