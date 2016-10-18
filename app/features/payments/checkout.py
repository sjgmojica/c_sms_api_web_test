'''
module to handle checkouts after being paid

@author: vincent agudelo


'''

from models.checkout import *
from models.account import *

import utils.add_sms_credits as credit_tool


from  utils.smart_payment_tool import is_successful as response_successful

import features.logging as sms_api_logger

from . import notification as payment_notif_tool

def on_payment_success( callback_response, checkout_id, account_id ):
    '''
    this executes the procedures done after a successful payment has been made
    
    this process should not be dependent on payment method
    '''
    l = sms_api_logger.PaymentLogger()

    # check if the json callback is a successful callbak

    good_response = response_successful( json_response=callback_response )
    l.info('payment response', good_response)
#     if not good_response :
#         return

    __process_on_payment_success(checkout_id=checkout_id, 
        account_id=account_id, good_response=good_response, l=l)
    
    #-- end

def on_payment_success_dragonpay(txn_id, good_response):
    '''
        @description:
            - handles the dragonpay callback
            - txn_id is just CHKID_<checkout_id>
    '''
    logger = sms_api_logger.PaymentLogger()
    logger.info('dragonpay callback')
    
    checkout_id = txn_id[6:]  # extracts only the checkout_id

    __process_on_payment_success(checkout_id=checkout_id, 
        account_id=None, good_response=good_response, l=logger)
    

def on_payment_success_paypal( checkout_id ):
    
    logger = sms_api_logger.PaymentLogger()
    logger.info('paypal callback')
    
    mycheckout=Checkout.get( checkout_id=checkout_id )
    __process_on_payment_success(checkout_id=checkout_id, account_id=mycheckout.account_id, good_response=True, l=logger)
    


def __process_on_payment_success(checkout_id, account_id, good_response, l):
    '''
        @description:
            - shared procedure used for different payment types
    '''
    
    checkout_object = Checkout.get( checkout_id=checkout_id)
    
    if not account_id:
        account_id = checkout_object.account_id
    
    if good_response :
    
        # load checkout
        
        account_object = Account.get( account_id=account_id )
        
        #step 1
        # update checkout table SUCCESS
        
        try:
            l.info('mark checkout as successful', {'checkout id': checkout_object.checkout_id })
            __mark_checkout_payment_successful( checkout_object ) 
        except Exception, e:
            l.error('unable to mark success', e)
        
        #step 2
        # if account is free/inactive, mark account to PAID
        
        if account_object.package_type != Account.PACKAGE_PAID :
            l.info('set account from FREE to PAID', {'account id': account_object.account_id })
            try:
              __update_account_type_to_paid( account_object )
            except Exception, e:
                #log error here
                l.error('unable to mark package to paid', e)
            
        # step 3
        # add credits to sms api
        try: 
            l.info('add credits to user', { "suffix": account_object.suffix, "amount" : checkout_object.amount })
            credit_trans_id = __add_credits_to_account( suffix=account_object.suffix, amount=checkout_object.amount, logger=l )
          
            if credit_trans_id :
                checkout_object.credit_trans_id = credit_trans_id
                # refresh balance in the object (auto clears flags if needed)
                account_object.refresh_credit_balance()
          
        except Exception, e:
            #log error here
            l.error( 'unable to add credits', e )
        
        # step 4 write to purchase history

            
            
        # send notification to user
        l.info('sending notifications')
        payment_notif_tool.notify_payment_successful( checkout_object=checkout_object, account_object=account_object )


    else:
        checkout_object.mark_payment_failed()
        checkout_object.status = Checkout.STATUS_FAILURE
        
    try:
        l.info('write to purchase history', {"checkout id": checkout_object.checkout_id })
        __write_purchase_history( checkout_object )
    except Exception, e:
        l.error('unable to write to purchase history', e)

        
    
def __mark_checkout_payment_successful( checkout_object ):
    '''
    marks the checkout to successfully paid
    '''
    # error will be raised in case of failure
    checkout_object.mark_successfully_paid()
    
    # remember to set the status in the object
    checkout_object.status = Checkout.STATUS_SUCCESS


def __update_account_type_to_paid( account_object ):
    '''
    updates account package to PAID. should only be called
    if current package is not "PAID"
    '''
    account_object.set_to_paid_package()
    
    


def __add_credits_to_account( suffix, amount, logger ):
    
    charging = Checkout.get_carrier_charging()
    
    logger.info( 'using current charging cost', charging )
    
    trans_id = credit_tool.add_credits( suffix=suffix, amount=amount, charging=charging )
    
    logger.info( 'credit transaction result', trans_id )
    
    return trans_id


def __write_purchase_history( checkout_object ):
    
    checkout_object.write_to_purchase_history()
    
    pass