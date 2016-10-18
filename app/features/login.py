'''
this feature handles login and logout functions

this application will support session ids. cleanup is required


this uses Account module to get information of user. uses password module to encrypt password
uses registration.email module to check email format


@author: vincent agudelo

'''

import features.registration.email as email_tool
import features.registration.password as password_tool

from models.account import Account 


def login( email, password ):
    '''
    setup login of user given email and password
    
    
    @raise IncorrectPassword: if password of Account does not match
    
    '''
    
    # check email format and return false if invalid
    if not email_tool.is_email_format_valid( email ):
        
        return False
    
    encrypted_password = password_tool.encrypt( password )
    
    if type(email) is unicode :
        email = email.encode('utf-8')
    
    if type(password) is unicode :
        password = password.encode('utf-8')
    
    valid_user = Account.get_user_by_login( email, encrypted_password ) 
    
    return valid_user