from models.account import *
from models.verification import Verification 

import features.registration.password as password_tool
import features.registration.email as reg_email_tool
from features.registration.spiels import SPIELS

import features.logging as sms_api_logger

def register_user( first_name, last_name, email, company_name, address, password, password_again='' ):
    

    # a collector of INLINE errors used for display
    errors = {}
    
    
    # for inline error empty input field
    
    if not email:
        errors['invalid_email'] = SPIELS['gerror']
    if not password:
        errors['invalid_password'] = SPIELS['gerror']
    if not password_again:
        errors['passwords_dont_match'] = SPIELS['gerror']
    
    
    l = sms_api_logger.GeneralLogger()
    l.info('start registration sequence', {'email': email})
    #check password
    if 'invalid_password' not in errors and password_tool.is_new_password_valid( password ) is False:
        l.error('invalid password format')
        errors['invalid_password'] = SPIELS['ierror3']
        # raise password_tool.InvalidPasswordFormat( 'invalid password format' )

    if 'passwords_dont_match' not in errors and password_again:
        # this checking is only used because this function
        # might still be used by others without this param
        
        if password != password_again:
            l.error('password do not match')
            errors['passwords_dont_match'] = SPIELS['ierror2']        

    # check email address if in valid format
    if 'invalid_email' not in errors and not reg_email_tool.is_email_format_valid( email ) :
        l.error('invalid email format')
        errors['invalid_email'] = SPIELS['ierror1']
        # raise reg_email_tool.InvalidEmailFormatError( )
        

    # this serves as input checking.
    # if error dict has content, display inline error
    # messages to user
    
    if errors:
        return errors

    encrypted_password = password_tool.encrypt(password)
    
    result = False
    
    new_user_account = Account()
    
    new_user_account.first_name = first_name
    new_user_account.last_name = last_name
    new_user_account.email = email
    
    new_user_account.company = company_name
    new_user_account.address = address
    new_user_account.password = encrypted_password


    # if duplicate email exists in database
    # check if that is pending or active
    # raise respective error

    try :
        pending_created = new_user_account.create_pending_account()
        
        if pending_created :
            l.info('pending user created', { 'email':email,   'account id': new_user_account.account_id})
            try :
            
                verifi_object = Verification.create_new_signup_verification( new_user_account.account_id, new_user_account.email )

                if verifi_object :
                    l.info('sending verification to email queue', {'code':verifi_object.code, 'email':verifi_object.email })
                    
                    verifi_object.add_email_to_reg_queue()
                
            except Exception, e:
                l.error('could not save pending user', e)
                # most likely the verification was not save
                # delete pending user and ask user to create again
                new_user_account.delete_if_pending( )
                raise AccountSaveException('unable to save verification object: %s. pending user id=%s deleted' % ( e, new_user_account.account_id) )

            result = True
    
    except DuplicateEmailException, e :
        
        # the same email exists in database
        # no more INSERT will execute from here
        # 
        # check what user that is
        suspected_account = Account.get_raw_info( email=email )
        
        if suspected_account.is_active() :
            #print 'suspected account is currently active'
            l.error('trying to register email of current active account')
            raise ActiveAccountAlreadyExisting( '%s is an active account; id=%s' % (email, suspected_account.account_id) )
        elif suspected_account.is_pending() :
            l.info('trying to register email of pending account', email)
            #get verification object
            verifi = Verification.get( email=email, account_id=suspected_account.account_id )
            
            #print 'suspected account is currently pending'
            raise PendingAccountAlreadyExisting( verifi )
        
    l.info('registration sequence end')
    return result