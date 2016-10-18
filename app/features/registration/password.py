'''
this module handles all password related function for chikka sms api
@author: vincent agudelo

'''



def is_valid_password_format( password='' ):


    minimum_password_length = 8
    maximum_password_length = 32
    allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    
    # length
    
    input_length = len(password)
    
    if input_length < minimum_password_length or input_length > maximum_password_length:
        return False
    
    #using allowed chars
    for p_char in password:
        if p_char not in allowed_chars :
            return False
        
        
    return True

def is_new_password_valid( new_password='' ):
    '''
    checks if new password is valid
    
    
    '''
    minimum_password_length = 8
    allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    
    
    
    # length
    if len(new_password) < minimum_password_length:
        return False
    
    #using allowed chars
    for p_char in new_password:
        if p_char not in allowed_chars :
            return False
        
        
    return True


def create_password_reset_verification( email ):
    '''
    a user can reset password in case user forgets. user is not logged in.
    
    1. creates a verification record category EMAIL with hash code to be sent in email
    
    2. queues/sends email to user containing verification info 
    
    '''
    pass

    

    
    
def allow_verify_password_reset( pasword_code ):
    '''
    initiate password change via verification code
    
    this will only determine if password change is allowed for code
    
    '''
    
    
    
    return False

def change_password( account_id, old_password, new_password ):
    '''
    a user can change passowrd when logged-in
    
    @param account_id: Integer the account id of the user
    @param old_password : the current password of the user 
    @return: Boolean if the password change was successful
    
    
    @raise InvalidPasswordFormat: on invalid password format
    @raise IncorrectPassword: in case user enters invalid OLD PASSWORD 
    @raise SavePasswordException : generic error when password cannot be saved for some reason
    
    '''  
    
    
    return True
    
    



def encrypt( password ):
    '''
    encrypts password before ssaving to databsae
    currently sha256 is the official encryption algorithm. no salt (yet)
    '''

    return __encrypt_by_sha256( password )


def __encrypt_by_sha256( input_string ):
    import hashlib
    
    hash = hashlib.sha256()
    hash.update(input_string)
    encrypted = hash.hexdigest()

    return encrypted

class InvalidPasswordFormat( Exception ):
    pass

class InvalidPasswordLength( Exception ):
    pass