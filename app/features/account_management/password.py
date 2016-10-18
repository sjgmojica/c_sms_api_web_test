'''
this feature hadles the password aspect of account management
it may use some modules like the password module of registration package


'''
from datetime import datetime
from models.account import Account
from features.registration import password as password_tool, email as email_tool


from features.registration.password import InvalidPasswordFormat

#inherit exceptions to avoid confusion
from features.registration.email import InvalidEmailFormatError
from models.account import AccountNotExist, PendingAccountAlreadyExisting, SameToOldPassword
from models.verification import Verification, VerificationExpired, MaxSendForgotPassword, VerificationError

spiels = {
          'email_sent' : 'We sent a verification request to your email',
          'invalid_format':'Your password should be at least 8 characters (a-z and 0-9).',
          'invalid_old_password':'You have entered an invalid password. Please check and try again.',
          'invalid_password_length' : 'Your password should be at least 8 characters (a-z and 0-9).',
          'invalid_code' : 'Your password link is invalid. Click <a href="/forgotmypassword">here</a> to resend another password link.',
          'not_match' : 'Passwords don\'t match.'
          }

def edit_password( account_id, old_password, new_password ):
    '''
    main feature function to change password
    @raise InvalidOldPassword: if old password is not equal to current password
    '''
    
    
    
    # invalid format of old password is considered invalid
    # to save processing
    if len(old_password) < 8 or len(old_password) > 32 :
        raise InvalidOldPassword('invalid old password. too short / too long')
    
    if password_tool.is_valid_password_format( password=old_password ) is not True :
        raise InvalidOldPassword('invalid old password. bad format') 
    
    # beyond this point we assume that the old password is likely in valid format
    #--- ----------------------------------------------------------------
    
    # before encrypting, new password length
    if len(new_password) < 8 or len(new_password) > 32 :
        
        raise password_tool.InvalidPasswordLength('invalid password length') 
    
    
    if password_tool.is_valid_password_format( password=new_password ) is not True :
        raise password_tool.InvalidPasswordFormat
    
    # check "new password" format 
    
    encrypted_old_password = password_tool.encrypt( password=old_password )
    encrypted_new_password = password_tool.encrypt( password=new_password )
    
    
    account_object = Account.get( account_id=account_id )
    
    if not account_object:
        raise Account.AccountNotExist('account does not exist')
        
    is_same = account_object.check_same_old_password( password= encrypted_old_password )
    
    if is_same and old_password == new_password:
        raise SameToOldPassword()
    
    if is_same is not True :
        raise InvalidOldPassword('invalid old password. not match')
    
    # password should be ok at this point
    result = account_object.save_new_password( new_password=encrypted_new_password )
    
    return result
    


def change_password_by_code( code, new_password ):
    '''
    resets the password given the verification code
    '''
    
    #check if password is valid
#     if len(new_password) < 8 or len(new_password) > 32 :
#         raise password_tool.InvalidPasswordLength('invalid old password. too short / too long')

    if password_tool.is_valid_password_format( password=new_password ) is not True :
        raise InvalidPasswordFormat('invalid format')


    verification_object = Verification.get_forgot_password_verify_by_code( code=code )
    #print verification_object


    account_object = Account.get( account_id=verification_object.account_id )
    
    if account_object :
        encrypted_new_password = password_tool.encrypt( password=new_password )
        result = account_object.save_new_password( new_password=encrypted_new_password )
        
        if result :
            verification_object.destroy()
            return True


    return False
    

def resend_forgot_password_by_code( code ):
    
    verification_object = Verification.get_forgot_password_verify_by_code( code=code )
    
    
    if verification_object :
        
        # step 1 update expiry
        verification_object.update_forgot_password_expiry()
        
        # step 2 add to email queue
        verification_object.add_forgot_password_email_to_queue()
    else :
        raise VerificationError('does not exist')
    

    
def forgot_password_send( email ):
    '''
    @param email: the email of the user to send the password
    executes process for "forgot password" procedure
    
    
    email is sent to email address identified by "email" parameter
    '''
    
    # 1. check if email is invalid or unregistered
    
    
    valid_email_format = email_tool.is_email_format_valid( email )
    if not valid_email_format:
        raise InvalidEmailFormatError()
    
    # check if email is registered 
    account_object = account = Account.get( email=email )
    if account_object is None :
        raise AccountNotExist('account does not exist')
    else :
        if account_object.is_pending() is True :
            raise PendingAccountAlreadyExisting()
        
        
    # verification will now be created
    
    verification_object = Verification.create_new_forgot_password_verification( account_object=account_object )
    
    if verification_object :
        verification_object.add_forgot_password_email_to_queue()
    
    
    
    
    
    
def is_valid_forget_password_code( code ):
    '''
    checks if code is valid
    @return: Boolean . if code is valid or not (exists in database and is PASSWORD-type verification)
    @raise VerificationExpired: on expired verification 
    
    '''
    
    verification_object = Verification.get_forgot_password_verify_by_code( code=code )
    if verification_object :

        # check if password verification is expired
        
        print 'expiry is', type(verification_object.date_expiry)
        if  verification_object.date_expiry < datetime.now() :
            raise VerificationExpired()
        
        
        return True
    
    
    
    
    else:
        return False
    
    
    
#AccountNotExist, PendingAccountAlreadyExisting    
    
class InvalidOldPassword( Exception ):
    pass
