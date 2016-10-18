'''
    @author: jhesed tacadena
    @description:
        - testmin.py contains functions
        that will be used for enrolling
        and testing mins
        - the functions that will be called by the
        handler are only the functions that do not
        start with "__", specifically, it starts
        with the word "process"
    @year: 2013
'''

from random import choice
from datetime import datetime
from ujson import loads
from models.account import Account
from models.verification import Verification, \
    DuplicateVerificationCodeException
from models.content_providers import ContentProviders
from features.testmin.exceptions import *
import features.logging as sms_api_logger
from utils.mobile_formatting_util import is_mobile_format_valid, \
    MobileNotSmartException, MobileNotGlobeException
from utils.text_api import send_pincode, send_generic_sms
from utils.determine_carrier import DetermineCarrier

MAX_CODE_REQUEST = 3
MAX_CODE_TRIES = 3
RANDOM_STRING = 'ABCDEFGHJKMNPQRTUVWXYZ2346789'
MAX_CHANGEMIN_CTR = 3
TESTMIN_CODE_REQUEST_KEY = 'code:request:user:%s:testmin:%s'


def process_testmin_enrollment(account_id, testmin):
    '''
        @description:
            - handles the processing of testmin
            enrollment
    '''
    
    gen_logger = sms_api_logger.GeneralLogger() 
    
    if not testmin:
        raise EmptyMinException()
    
    if not is_mobile_format_valid(testmin):
        gen_logger.error('testmin enrollment -- invalid mobile', 
            {'account_id': account_id, 'mobile': testmin})
        raise InvalidTestminException(testmin)
    
    testmin = '639%s' %str(testmin[-9:])
    
    # ! TEMPORARY FIX ! 
    # while there is a problem
    # on SMART
    # uncomment after problem is fixed
    
    dt = DetermineCarrier(testmin)
    
    # if dt.get_carrier() == 'SUN':   
        # should be MobileNotSupportedException in the future
        # raise MobileNotGlobeException(account_id, testmin)
    
    # END TEMPORARY FIX
    
    if __has_reached_max_unver_testmins(
        account_id, testmin):
        gen_logger.error('testmin enrollment -- max unverified testmin enrollments', 
            {'account_id': account_id, 'mobile': testmin})
            
        raise MaxUnverifiedMinEnrollmentsException(account_id)
        
    acct_obj = Account.get(account_id=account_id)
    if __was_testmin_prev_verified(acct_obj, testmin):
        gen_logger.error('testmin enrollment -- testmin previously verified', 
            {'account_id': account_id, 'mobile': testmin})
            
        raise TestminPreviouslyVerifiedException(
            account_id, testmin)
            
    if __has_reached_max_changemin(acct_obj):
        gen_logger.error('testmin enrollment -- changed testmin more than allowed', 
            {'account_id': account_id, 'mobile': testmin})
            
        raise MaxChangeMinException(account_id) 
        
    if __has_reached_max_code_request(account_id, testmin):
        gen_logger.error('testmin enrollment -- max code request for the day', 
            {'account_id': account_id, 'mobile': testmin})
            
        raise MaxCodeRequestsException(account_id, testmin)

    correct_code = __generate_code(account_id)
    verification_id = __save_code(account_id, correct_code, testmin)
    
    #message_id = send_pincode(account_id, testmin, str(correct_code)) # text api call
    sms_body = 'Welcome to CHIKKA API!\n\nYour pin code is %s. Enter this code to the site to verify your account. This msg is free.' % str(correct_code)
    message_id = send_generic_sms( phone=testmin, body=sms_body )
    
    
    gen_logger.info('testmin enrollment -- sending pincode (using API)', 
        {'account_id': account_id, 'mobile': testmin, 'message_id': message_id, 'code': correct_code})
    
    return verification_id   
     
 
def process_testmin_code_verification(
    suffix, account_id, testmin, code):
    '''
        @description:
            - handles testmin code verificition
    '''
    
    gen_logger = sms_api_logger.GeneralLogger() 
     
    testmin = '639%s' %str(testmin[-9:])
    
    correct_code = __get_vercode(account_id, testmin)
    
    if not __is_code_correct(correct_code, code):
        gen_logger.error('testmin enrollment -- incorrect pincode', 
            {'account_id': account_id, 'mobile': testmin,
            'code': code, 'suffix': suffix})
            
        raise WrongCodeException(account_id, testmin, code) 
         
    if __is_code_expired (correct_code) and \
        __has_reached_max_code_request(account_id, testmin):    
        
        gen_logger.error('testmin enrollment -- expired pincode, max code requests', 
            {'account_id': account_id, 'mobile': testmin,
            'code': code, 'suffix': suffix})
                  
        raise ExpiredCodeMaxCodeRequestException(account_id, testmin, code)
    if __is_code_expired (correct_code):    
    
        gen_logger.error('testmin enrollment -- expired pincode', 
            {'account_id': account_id, 'mobile': testmin,
            'code': code, 'suffix': suffix})
                  
        raise ExpiredCodeException(account_id, testmin, code)
            
    
    __save_testmin(account_id, testmin)
    ContentProviders.update_cached_api_min(suffix, testmin)
    
    Verification.delete_mobile_code(account_id, testmin)
    
def process_testmin_code_resend(account_id, 
    testmin=None, ver_id=None):
    '''
        @description:
            - handles the resending of 
            verification code
    '''
    # if not testmin and ver_id:
        # testmin = __get_min(account_id, ver_id)
    
    gen_logger = sms_api_logger.GeneralLogger() 
    
    if testmin:    
        testmin = '639%s' %str(testmin[-9:])
        
    if __has_reached_max_code_request(account_id, testmin):
        gen_logger.error('testmin enrollment -- max pincode resends', 
            {'account_id': account_id, 'mobile': testmin})
        raise MaxCodeRequestsException(account_id, testmin)
    
    correct_code = __get_vercode(account_id, testmin)['code']
    
    send_pincode(account_id, testmin, str(correct_code))
    gen_logger.info('testmin enrollment -- resending pincode (using API)', 
            {'account_id': account_id, 'mobile': testmin})
    
    __save_code(account_id=account_id, ver_id=ver_id) # updates expiry date
    return testmin
    
      
# **************************************
# **************************************
# PRIVATE functions. Use with care
# **************************************
# **************************************


# --------------------------------------
#  Used by process_testmin_enrollment 
# --------------------------------------
        
def __has_reached_max_unver_testmins(account_id, testmin):
    '''
        @description:
            - returns True if the user enrolled 
            unverified testmin more than the 
            allowed (per day), else False
            - updates array of 
    '''
    testmin = '639%s' %str(testmin[-9:])

    unver_req = Verification.get_code_unverified_requests(
        account_id)
    
    if not unver_req:
        # return False and create redis list 
        # (for counting and comparison)
        unverified_mob_list = [testmin]
        Verification.set_code_unverified_requests(
            account_id, unverified_mob_list)
        return False
    
    unver_req = loads(unver_req)
  
    if unver_req and len(unver_req) >= MAX_CODE_REQUEST and \
        testmin not in unver_req:
        return True
    
    if testmin not in unver_req:
        unver_req.append(testmin)
        Verification.set_code_unverified_requests(
            account_id, unver_req)
     
    return False
        
def __has_reached_max_changemin(acct_obj):
    '''
        @description:
            - determines if user changed his/her 
            textmin more that the allowed
            times, during the trial period 
            (i.e. more than 3 changes)
            - uses accounts table
    '''
    if acct_obj and int(acct_obj.change_mobile_ctr) >= MAX_CHANGEMIN_CTR:
        return True
    return False
    
    
def __was_testmin_prev_verified(acct_obj, testmin):  
    '''
        determines if the testmin of the user
        was previously verified
    '''
    testmin = '639%s' %str(testmin[-9:])
    
    if acct_obj:
        if acct_obj.test_min == testmin:
            return True
    return False
                
def __has_reached_max_code_request(account_id, testmin):
    '''
        @description:
            - returns True if user requested 
            code for than the allowed times,
            else False
    '''
    
    testmin = '639%s' %str(testmin[-9:])
    
    request_count = Verification.incr_code_request_count(
        account_id=account_id, testmin=testmin)

    if request_count and int(request_count) > (MAX_CODE_REQUEST):
        return True
    return False

def __generate_code(account_id):
    '''
        returns a random 
        verification code
    '''
    is_unique = False
    rand_code = ''.join(choice(RANDOM_STRING)
            for i in range(6))
    return rand_code
            
def __save_code(account_id, code=None, testmin=None, ver_id=None):
    '''
        saves the code generated
        in the Verification table
    '''
    if testmin:
        testmin = '639%s' %str(testmin[-9:])

    gen_logger = sms_api_logger.GeneralLogger() 
    
    try:    
        ver_obj = Verification.get_mobile_code(
            account_id=account_id, testmin=testmin)
        
        if ver_obj or ver_id:
            if not ver_id:
                ver_id = ver_obj['id']
                
            if code: 
                Verification.update_mobile_code(
                    account_id=account_id, code=code,
                    mobile=testmin, ver_id=ver_id)
            else:
                Verification.update_mobile_code(
                    account_id=account_id, 
                    mobile=testmin, ver_id=ver_id)
            
            
            gen_logger.info('testmin enrollment -- updating pincode', 
                {'account_id': account_id})
               
            return ver_obj['id'] if not ver_id else ver_id
        else:   
            
            gen_logger.info('testmin enrollment -- saving pincode', 
                {'account_id': account_id, 'pincode': code})
                
            return Verification.save_mobile_code(
                account_id=account_id, code=code,
                mobile=testmin)
                
    except DuplicateVerificationCodeException, e:        
        gen_logger.info('testmin enrollment -- pincode not unique', 
            {'account_id': account_id, 'error': str(e)})
        save_code(account_id, code, testmin)
    except Exception, e:
        gen_logger.error('testmin enrollment -- unable to save pincode', 
            {'account_id': account_id, 'error': str(e)})
        print e
      
# -------------------------------------------
# Used by process_testmin_code_verification 
# -------------------------------------------
 
def has_reached_max_wrong_code_tries(account_id, testmin):
    '''
        @description:
            - returns True if user has inputted
            wrong codes more than allowed,
            else False 
            - uses redis incr
    '''
  
  
    testmin = '639%s' %str(testmin[-9:])
    
    code_tries = Verification.incr_code_tries(
        account_id=account_id, testmin=testmin)        
    # if code_tries and int(code_tries) > MAX_CODE_TRIES:
    gen_logger = sms_api_logger.GeneralLogger()    
    gen_logger.info('testmin enrollment -- max pincode retries',
        {'account_id': account_id, 'mobile': testmin})
        # return True
    # return False
    
    if code_tries:
        return int(code_tries)
    return None

def __get_vercode(account_id, testmin):
    '''
        @description:
            - returns the verification code
    '''
    
    testmin = '639%s' %str(testmin[-9:])
    
    correct_code = Verification.get_mobile_code(
        account_id=account_id, testmin=testmin)   
    return correct_code
       
def __is_code_correct(correct_code, code):
    '''
        @description:
            - returns True if code is correct,
            else False
    '''
    if not correct_code:
        return False
    
    if str(correct_code['code']).lower() != str(code).lower():
        return False
    return True

def __is_code_expired(correct_code):
    '''
        @description:
            - returns True if code is expired,
            else False
    '''
    if correct_code and 'date_expiry' in correct_code:    
    
        if datetime.now() > correct_code['date_expiry']:
            return True
    return False
       
    
def __save_testmin(account_id, testmin):
    '''
        Save the testmin into
        the Accounts table
    '''
    
    testmin = '639%s' %str(testmin[-9:])
    
    return Account.save_testmin(
        account_id=account_id, testmin=testmin)

def get_min(account_id, ver_id):
    min = Verification.get_min(account_id, ver_id)
    if min and 'mobile' in min:
        return min['mobile']
