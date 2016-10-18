'''
@author: vincent agudelo
this is the module to handle re-sending of SMS (with code) during smart payment gateway payment


back story
if a user selects to pay the checkout using Smart Payment Gateway, he is prompted to input the
SMART(network) MOBILE NUMBER where credits are to be deducted. an SMS will be sent to that
mobile number with a unique auto-generated code. that code will be used to verify the payment
by user input to a displayed form.

resend sms is a new feature where the sms sent to the user WILL BE SENT AGAIN but with the
following conditions
'''
from datetime import datetime, timedelta


resend_time_limit = timedelta( minutes=25)

max_sms_resend = 3



from models.checkout import SmartPaymentGatewayCheckout, CheckoutNotExistError

from gevent.pool import Pool

def resend_sms( checkout_id ):
    '''
    function to resend the sms
    
    '''
    
    # get information on the involved checkout
    
    #check if the input checkout id is a valid id format (integer)
    try:
        checkout_id = int(checkout_id)
    except Exception, e:
        raise CheckoutNotExistError( 'invalid checkout id [%s] : %s' % ( repr(checkout_id), e   ) )
    
    
    
    checkout_object = SmartPaymentGatewayCheckout.get( checkout_id=checkout_id )
    
    if checkout_object :
        
        
        # verify that the checkout is in NULL state
        if checkout_object.status != None :
            raise NonPendingCheckoutResendSmsError('checkout id [%s] is NOT a PENDING checkout' % checkout_id )
        
        # check if checkout is an expired checkout
        if checkout_object.date_expiry  <= datetime.now() :
            raise ResendNotSupported('checkout with id [%s] is expired' % checkout_id )
            
        
        # check if resend counter is at max
        if checkout_object.sms_resend_ctr >= max_sms_resend:
            raise MaxResendReachedError( 'max resend reached, counter at %s' % checkout_object.sms_resend_ctr )

        # check if resend time limit has passed (25 minutes from checkout creation)
        if ( datetime.now() - checkout_object.date_created ) > resend_time_limit :
            raise ResendTimeLimitReached('time limit [%s] for resend reached. checkout created %s' % (resend_time_limit, checkout_object.date_created) )
        
        
        # execute code asynchronously
        job_pool = Pool( 4 )
        job_pool.spawn( checkout_object.resend_payment_PIN_code  )
        
        
        
    else:
        # there is no such checkout
        raise CheckoutNotExistError('smart payment checkout with id [%s] does not exist' % checkout_id)
        
        
    
    
    
    

class ResendSMSError( Exception ):
    '''
    base exeption that defines that the exception
    came about from an error in resending sms
    '''
    pass

class MaxResendReachedError( ResendSMSError ):
    '''
    there is a limit to a number of times where a user can request resend sms 
    this should be thrown to identify the particular error
    '''
    pass

class ResendTimeLimitReached( ResendSMSError ):
    '''
    there is a limit to up to when a user can request sms resend after the first sms was sent
    '''
    
    pass

class NonPendingCheckoutResendSmsError( ResendSMSError ):
    '''
    should be rasied when resend sms is done on non-pending checkout
    '''
    pass

class ResendNotSupported( ResendSMSError ):
    '''
    only some checkout payment methods allow resend sms code
    i.e. smart payment gateway
    
    can also be used to indicate that the checkout can no longer be used to resend
    i.e. status not Null, checkout is expired
    
    '''
    
    pass 