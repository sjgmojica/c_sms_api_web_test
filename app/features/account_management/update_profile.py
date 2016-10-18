'''
    @author: Jhesed Tacadena
    @date: 2013-11
'''

from models.account import Account
from utils.html_sanitizer import sanitize_html

import features.registration.email as reg_email_tool

def update_profile(account_id, firstname, lastname, address, company):
    firstname = sanitize_html(firstname)
    lastname = sanitize_html(lastname)
    address = sanitize_html(address)
    company = sanitize_html(company)
    
    Account.update(account_id=account_id,
        firstname=firstname, lastname=lastname, 
        address=address, company=company)
    

def update_name( account_object, name ):
    '''
    upates tenae fild of given user
    '''
    
    account_object.update_name( name=name )
    
    
def change_billing_email( account_object, new_billing_email=None ):
    # default
    result = False
    
    if new_billing_email:
        
        if reg_email_tool.is_email_format_valid( new_billing_email ):
            account_object.change_billing_email( billing_email=new_billing_email )
            result = True
        
        #else must be invalid email format 
        
        
    else:
        print 'empty email'
        result = False
        
        
    return result