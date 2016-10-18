'''
stores payment methods

@author: vincent agudelo

'''
import gevent
from models.checkout import Checkout
import random
import string

import utils.smart_payment_tool as smart_payment
import features.logging as sms_api_logger

from features.paypal.paypal_api_tools import PaypalExpressCheckout 
from features.paypal.paypal_main import set_paypal_checkout_pending

from features.paypal.paypal_checkout_model import PaypalPaymentCheckout

from features.paypal.paypal_utils import get_paypal_callback_hash

def pay_via_smart_payment( checkout_id ):
    '''
    wrapper for paying via smart payment gateway
    @return: Boolean , payment sucess
    '''

    payment_success = False

    payment_logger = sms_api_logger.PaymentLogger()
    
    payment_logger.info('executing payment via SMART PAYMENT GATEWAY')
    
    max_tries = 3
    
    # step 1 load checkout object
    checkout_object = Checkout.get_for_payment( checkout_id=checkout_id )

    if checkout_object :
        
        payment_logger.info('reference checkout id', checkout_id )
         
        callback_params = {'cid':checkout_object.checkout_id , 'aid':checkout_object.account_id}
    
        # step 2 call EJ api and pay amount using checkout data
        # retry 3 times
        # log on error
        
        # generate transactionid
        trans_id = '%s:%s' % (checkout_object.checkout_id, ''.join(random.choice( 'ABCDEFGHJKMNPQRSTUVWXYZ23456789' ) for x in range(6)))
        
        success = False
        try_run = 1
        result = None
        while success is False and try_run <= max_tries:
            
            try:
                payment_logger.info('try %s : sending payment' % try_run, { 'payment_trans_id': trans_id,   'amount': checkout_object.amount,  'callback_params':callback_params  })
                result = smart_payment.execute_payment( min=checkout_object.phone, amount=checkout_object.amount,  trans_id=trans_id, callback_params=callback_params )
                payment_logger.info('gateway result', result )
                
            except Exception, e:
                payment_logger.error('exception raised while paying: %s' % e , repr(e))
                gevent.sleep(1)
            else:
                
                if not result :
                    payment_logger.error('payment FAILED')
                    gevent.sleep(1)
                else:
                    success=True
                    payment_logger.info('payment successful!!!')
                    payment_success = True
            finally:
                try_run+=1
                if not success :
                    payment_logger.error('payment FAILED', {'checkout id':checkout_id})
                    
                else:
                    payment_logger.info('payment successfully sent to smart payment', {'checkout id':checkout_id})
    else:
        payment_logger.error('checkout with id=%s is not valid for payment. may already be paid' % checkout_id, checkout_id )
                    
    return payment_success



def get_paypal_expresscheckout_url( checkout_id ):
    
    print 'execute pay via paypal'
    url=None
    
    checkout_object = Checkout.get_for_payment( checkout_id=checkout_id )
    checkout_items = checkout_object.get_checkout_items() 
    # instantiate paypal tool
    
    paypal_api_caller = PaypalExpressCheckout()
    
    if checkout_items :
        for c_item in checkout_items: 
            paypal_api_caller.add_checkout_item(desc= c_item['desc'] , cost=c_item['cost'], qty=c_item['qty'])
    

        hash = __get_paypal_callback_hash( account_id=checkout_object.account_id, checkout_id=checkout_id )
        paypal_api_caller.set_express_checkout( callback_uri='/paypal/confirm/%s/%s'% (hash, checkout_id), custom_params={ 'checkout_id':checkout_id }  )
        if paypal_api_caller.transaction_success is True:
            print 'set checkout success'
            url = paypal_api_caller.get_paypal_checkout_url()
        else:
            raise PaypalModuleError('unable to get express checkout from paypal: %s' % paypal_api_caller.general_error_msg )
            
    else:
        print 'no checkout items'

    return url
def receive_paypal_callback( token, account_id, checkout_id, hash ):
    '''
    evaluates the hash given before executing the payment
    
    returns checkout object for reference purposes
    
    '''
    
    correct_hash = __get_paypal_callback_hash( account_id=account_id, checkout_id=checkout_id )
    
    if hash == correct_hash:

        # set checkout to pending
        checkout_object = PaypalPaymentCheckout.get(  checkout_id=checkout_id )
        
        if checkout_object :
            
            if checkout_object.status == PaypalPaymentCheckout.STATUS_PENDING:
                set_paypal_checkout_pending( checkout_object=checkout_object )
                return checkout_object
            else :
                # raise exception invalid checkout
                raise PaypalPaymentError( 'checkout [%s] is no longer pending' % checkout_id )
        else:
            raise PaypalPaymentError( 'checkout [%s] does not exist' % checkout_id )
    else:
        raise PaypalPaymentError( 'hash used is not correct; checkout_id=%s input_hash=%s' % ( checkout_id, hash ) )
    

def __get_paypal_callback_hash( account_id, checkout_id ):
    return get_paypal_callback_hash( account_id=account_id, checkout_id=checkout_id )

class PaypalModuleError( Exception ):
    pass

class PaypalPaymentError( PaypalModuleError ):
    pass