'''
this module is in charge of changing email of a user

'''

from models.account import *
from models.verification import *

from datetime import timedelta


from features.registration import email as base_email_tool 

from features.registration.email import InvalidEmailFormatError

import features.logging as sms_api_logger_tool

def change_email( account_object, new_email ):
    '''
    @param account_id : the account id of user that changes the email
    @param new_email: the proposed new email
    
    @raise ActiveAccountAlreadyExisting : raised when proposed email is owned by existing pending account 
    @raise PendingAccountAlreadyExisting : raised when proposed email is owned by existing active account 
    '''

    logger = sms_api_logger_tool.GeneralLogger()
    
    logger.info('processing change email request', {'account_id':account_object.account_id, 'new_email':new_email})

    # check format
    if not new_email or not base_email_tool.is_email_format_valid( new_email ) :
        logger.error('email has invalid format')
        raise InvalidEmailFormatError( 'invalid email format' )
    
    if account_object.email == new_email :
        logger.error('user is using the same email as current')
        raise SameEmailError()
    
    success = True
    
    #step 1
    # check if email is existing (pending or active)
    raw_account = Account.get_raw_info( email=new_email )
    if raw_account :
        
        # check if active
        if raw_account.is_active():
            logger.error('email already exists in an active account')
            raise ActiveAccountAlreadyExisting()
            
        elif raw_account.is_pending():
            # get pending verification
            verifi = Verification.get( account_id=account_object.account_id, email=new_email, category='SIGNUP' )
            if verifi:
                raise PendingAccountAlreadyExisting(verifi)
            else:
                raise PendingAccountAlreadyExisting()
            
        # check if pending
    else:
        # check if existing change email verification exists
        # coming from the same user
        verifi = Verification.get( account_id=account_object.account_id, email=new_email, category='CHANGEEMAIL' )
        
        if verifi :
            raise ChangeEmailVerifyExists( verifi )
            # existing
            # should inform
            pass
        else:
            #write new verification record
            
            expiration_delta = timedelta( hours=48 )
            new_email_vferifi = Verification.create_new_change_email_verification( account_object=account_object, new_email=new_email, expiration_delta=expiration_delta )
            
            # send email to queue
            new_email_vferifi.add_changeemail_to_email_queue()

    return success


def verify_change_email( code ):
    
    verifi = Verification.get_change_email_verification_by_code( code=code, resend_code=None )
    
    if verifi :
        
        if verifi.is_expired() :
            raise VerificationExpired()
        
        account_object = Account.get( account_id=verifi.account_id )
        #if account_object.change_email( email )
        if account_object :
            #change_email
            account_object.change_email( new_email=verifi.email )
            
            # destroy verification
            verifi.destroy()
    else :
        raise NoVerificationError('verification with code %s does not exist' % code )
            
            
def resend_change_email_verify( resend_code ):
    
    verifi = Verification.get_change_email_verification_by_code( code=None, resend_code=resend_code )
    
    if verifi :
        
        account_object = Account.get( account_id=verifi.account_id )
        
        if account_object :
            
            Verification.set_send_status_null( verification_id=verifi.verification_id )
            verifi.add_changeemail_to_email_queue()
            
            verifi.update_signup_expiry()
            
        else: 
            raise VerificationError()
            
    else :
        raise VerificationError()