'''
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - encapsulates the api management
        process to the calling handler
'''

import M2Crypto
import base64
import hashlib
from features.api_management.exceptions import *
from features.api_management.spiels import SPIELS
import features.logging as sms_api_logger
from models.content_providers import ContentProviders
from utils.url_tools import is_url_valid
from utils.authentication import validate_signature

def process_api_update(account_obj, public_key, 
    callback_url, mo_url):
    '''
        @description:
            - processes the updating of 
            API settings
            - process:
            validate inputs -> update content provider table
            - does not follow try except format
            because it will be used in ajax call
    '''
    gen_logger = sms_api_logger.GeneralLogger()    
    account_id = account_obj.account_id
    suffix = account_obj.suffix

    # returns a dict of errors instead of raising
    # individual exceptions because the error_message
    # may not be only 1, and displayed as inline message
    # (i.e. using js)

    response = {
        'has_error' : False,
        'success_message': SPIELS['success1']
    }
    ERRORS  = {
        'public_key': None,
        'callback_url': None,
        'mo_url': None
    }

    # validations
    
    """
    if not __is_public_key_valid(public_key):
        gen_logger.error('invalid public key', 
            {'account_id': account_id, 'public_key': public_key})
            
        ERRORS['public_key'] = SPIELS['error1']
        response['has_error'] = True
        # raise InvalidPublicKeyException(
            # account_id, suffix, public_key)
    """
    
    if callback_url != ' ' and not __is_callback_url_valid(callback_url):
        gen_logger.error('invalid callback url', 
            {'account_id': account_id, 'callback_url': callback_url})
       
        ERRORS['callback_url'] = SPIELS['error3']
        response['has_error'] = True
        # raise InvalidCallbackUrlException(
            # account_id, suffix, callback_url)
            
    if mo_url != ' ' and not __is_mo_url_valid(mo_url):
        gen_logger.error('invalid mo url', 
            {'account_id': account_id, 'mo_url': mo_url})
              
        ERRORS['mo_url'] = SPIELS['error2']
        response['has_error'] = True
        # raise InvalidMoUrlException(
            # account_id, suffix, mo_url)
    
    if not response['has_error']:

        # process updating of API settings
        
        # ContentProviders.create(suffix=suffix,
            # public_key=public_key, mo_url=mo_url,
            # callback_url=callback_url, 
            # testmin=account_obj.test_min)
        
        # saves the API content to INFRA team's redis
        
        ContentProviders.update_cached_api_settings(
            suffix=suffix,
            public_key=public_key, mo_url=mo_url,
            callback_url=callback_url, 
            testmin=account_obj.test_min)  
    
    response['errors'] = ERRORS
    return response
    
def get_content_provider_obj(account_obj):
    '''
        @description:
            - returns content_object_provider
            for display purpose
    '''
    return ContentProviders.get(account_obj.suffix)
  
  
def validate_rsa_signature(account_suffix, message, signature):
   
    gen_logger = sms_api_logger.GeneralLogger()  
    response = {
        'error': False,
        'message': SPIELS['success2']
    }
    content_provider = ContentProviders.get(account_suffix)
    # if not content_provider or content_provider == ' ':
        # response['error'] = True
        # response['message'] = SPIELS['error5']
        # return response
     
    if not content_provider or 'PUBLIC_KEY' not in content_provider or \
        content_provider['PUBLIC_KEY'] == ' ':   
        response['error'] = True
        response['message'] = SPIELS['error5']    
        return response
    
    public_key = content_provider['PUBLIC_KEY']
    if not validate_signature(public_key, signature, message):
        gen_logger.error('RSA signature invalid', 
            {'suffix': account_suffix, 'signature': signature})
        
        response['error'] = True
        response['message'] = SPIELS['error4']    
        return response 
    
    gen_logger.info('SUCCESS RSA signature validation', 
            {'suffix': account_suffix, 'signature': signature})
         
    return response
    
    
# *****************************
# PRIVATE FUNCTIONS 
# use with care
# *****************************
    
def __is_public_key_valid(public_key):
    # insert validation here
    if not public_key:
        return False
    return True
    
def __is_callback_url_valid(callback_url):
    return is_url_valid(callback_url)
    
def __is_mo_url_valid(mo_url):
    return is_url_valid(mo_url)