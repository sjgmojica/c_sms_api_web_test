'''
this module is in charge of email verification

@author: vincent agudelo
'''

from models.verification import *
from models.account import Account

from datetime import datetime


def verify_signup_email( code ):
    
    success = False
    
    verifi = Verification.get( code=code )


    if verifi and verifi.account_id :
        
        # get associated account
        associated_account = Account.get( account_id = verifi.account_id  )
        
        if associated_account :
            
            current_datetime = datetime.now()
            
            if current_datetime > verifi.date_expiry :
                raise VerificationExpired()


            # make sure account is not expired
        
            Account.set_active( account_id =verifi.account_id  )
            # delete verification record
            verifi.destroy()
             
            success = verifi.account_id
        
    
    
    return success


def resend_verification_email( code ):
    '''
    this function re-sends email (send to queue)
    
    as per business rule a user has a maximum of 10 resends per email per day
    '''
    max_retries_per_day = 10
    result = False
    
    verification_object = Verification.get( resend_code=code )
    if verification_object :
        # make sure there is associated account
            # get associated account
        associated_account = Account.get( account_id = verification_object.account_id  )
        
        if associated_account :

            # step 1 increment the resend counter and evaluante
            retries = verification_object.increment_resend_tries()
            
            if retries <= max_retries_per_day :
                
                # reset send status
                Verification.set_send_status_null( verification_id=verification_object.verification_id )
                
                # step 2 send email to queue if evaluated OK
                verification_object.add_email_to_reg_queue()
                
                # step 3 update date expiry
                verification_object.update_signup_expiry()
                result = True

    
    return result    