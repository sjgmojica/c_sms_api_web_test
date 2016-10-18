'''
contains general profedures for paypal payment system 


@author: vincent agudelo

'''

import gevent
from gevent.pool import Pool
from . import mysql_dao, max_purchase_value_per_month
from datetime import datetime, timedelta

from .paypal_token_model import PaypalToken

import time
from features.paypal import paypal_api_tools
from features.paypal.paypal_utils import get_paypal_callback_hash
from features.payments.checkout import on_payment_success_paypal
import copy

from . import paypal_settings
from . import email_sending_config


from models.checkout import Checkout
from models.account import Account
from .paypal_checkout_model import PaypalPaymentCheckout
from features.logging import PaymentLogger

from utils.send_mailx import send_mailx


# sample limit
allowed_purchases_per_month = max_purchase_value_per_month

def is_within_allowed_paypal_purchases( account_id, amount, current_purchases=None ):
    '''
    general function to be called for determining if account can purchase given amount using PAYPAL
    for now this just checks if the accumulated successful  purchases via PAYPAL will exceed the configured
    maximum amount.
    
    this is computed by fetching the recorded purchases and adding it to the amount the account plans to purchase
    
    so if the limit is 300000 Pesos
    
    and account purchased 299500 this month
    
    if account plans to purchase 500 Pesos via paypal then
    299500 + 500 = 300000
    
    still within legal bounds
    
    but if account plans to purchase 1000 instead
    299500 + 1000 = 300500
    
    this exceeds the 300000 limit and is not allowed for checkout. account should use a different payment method 
     
    
    in case you want to feed the current purchases manually, use current_purchases
    
    '''
    if current_purchases is not None:
        total_paypal_purchases = current_purchases
    else:
        total_paypal_purchases = get_total_paypal_purchases_for_current_month( account_id=account_id )
    
    if float(total_paypal_purchases)+float(amount) > allowed_purchases_per_month:
        is_within_allowed_purchase_value = False
    
    else:
        is_within_allowed_purchase_value = True


    return is_within_allowed_purchase_value
    
        
def get_total_paypal_purchases_for_current_month( account_id ):
    
    total_purchases = PaypalPaymentCheckout.get_total_purchases_current_month( account_id )

    return total_purchases


def set_paypal_checkout_pending( checkout_object ):
    
    checkout_id = checkout_object.checkout_id
    
    token_object = PaypalToken.get( checkout_id=checkout_id )
    token_object.set_pending()
    
    # set flag in cache to indicate pending paypal payment
    # life is 10 minutes
    checkout_object.set_paypal_pending_payment_flag()

def has_pending_paypal_purchase( account_id ):
    
    pending = PaypalPaymentCheckout.get_paypal_pending_payment_flag( account_id=account_id )
    
    if pending:
        return True
    else:
        return False
    
    
def set_paypal_checkout_failure( token ):
    
    mysql_dao.set_fail( token=token )


def run_payment():
    
    job_pool = Pool( 20 )
    
    logger = PaymentLogger()
    logger.info('INITIALIZE. paypal payment offline app')
    sleep_time = 5
    
    while True : # just keeps going and going
        
        paypal_express_checkout_tool = paypal_api_tools.PaypalExpressCheckout()
        
        try:
            pending_token = PaypalToken.get_one_pending()
            print 'pending', pending_token
            
            if pending_token :
                
                #set the status to CHARGING to prevent the record from being picked up but latter iterations
                if pending_token.set_charging():
                    # if statement makes sure that the query took effect
                    paypal_express_checkout_tool.set_token_obj( pending_token )
                    job_pool.spawn( process_individual_payment, express_checkout_obj=copy.deepcopy(paypal_express_checkout_tool)  )

        except Exception, e:
            logger.error('paypal application ERROR: %s' % e)
            print 'exception raised while performing request. %s' % e

        #--- manually cleanup
        paypal_express_checkout_tool=None
        del(paypal_express_checkout_tool)
        time.sleep( sleep_time )    
        
        
def process_individual_payment( express_checkout_obj ):
    
    
    logger = PaymentLogger()
    try:

        checkout_id = express_checkout_obj.express_checkout_token_obj.checkout_id 
        
        
        checkout_object = PaypalPaymentCheckout.get( checkout_id=checkout_id )
        
        logger.info('starting paypal payment process', {'checkout_id':checkout_id })
        
        try:
            details_result = express_checkout_obj.get_express_checkout_details( )
            
        except paypal_api_tools.UnverifiedUserException, e:
            logger.error('unverified user detected: %s' % e)
            # mark redis flag
            try:
                express_checkout_obj.express_checkout_token_obj.set_unverified_user_payment()
            except Exception ,e :
                logger.error('could not set cache flag: %s'%e )
                
            #--- SEND EMAIL TO USER
            account = Account.get( account_id = checkout_object.account_id )
            send_email_unverified_user_error( to_=account.email, checkout_id=checkout_id )

        except Exception, e:
            # send error email here
            account = Account.get( account_id = checkout_object.account_id )
            
            send_email_paypal_failed( to_=account.email, checkout_id=checkout_id )
            
            logger.error('exception raised while get express checkout info: %s' % e)
        
        if express_checkout_obj.transaction_success is True :
            
            if express_checkout_obj.ready_for_payment is True:
                logger.info('execute payment')
                
                try :
                
                    express_checkout_obj.do_express_checkout_payment()
                    
                    if express_checkout_obj.transaction_success is True :
                        logger.info('payment success. trying to add credits')
                        on_payment_success_paypal( checkout_id=express_checkout_obj.express_checkout_token_obj.checkout_id )
                        logger.info('add credit process done')
                        
                        # add credits to monthly paypal cache
                        increment_monthly_paypal_total_by( account_id=checkout_object.account_id, date_reference=datetime.now(), amount=checkout_object.amount )
                        
                        
                        
                        
                    elif express_checkout_obj.transaction_success is False :
                        set_failed_purchase( express_checkout_obj=express_checkout_obj, logger=logger )
                        logger.error( 'payment failure: %s; %s' % (express_checkout_obj.short_message, express_checkout_obj.long_message)  )
    
                except Exception, e:
                    
                    logger.error('unable to execute payment: %s' % e )
                
            else :
                logger.error( 'checkout will not be be paid; checkout status is [%s]' % express_checkout_obj.checkout_status )
                # set failed
                express_checkout_obj.express_checkout_token_obj.set_failed()
                set_failed_purchase( express_checkout_obj=express_checkout_obj, logger=logger )
    
        elif express_checkout_obj.transaction_success is False :
            set_failed_purchase( express_checkout_obj=express_checkout_obj, logger=logger )
            logger.error( 'get detail failure: %s; %s' % (express_checkout_obj.short_message, express_checkout_obj.long_message) )

        # after all operations, clear the pending payment flag
        # whether failed or successful
        try:
            checkout_object.clear_paypal_pending_payment_flag()
        except Exception, e:
            logger.error('unable to clear pending payment flag: %s' % e )



    except Exception, e:
        logger.error('error occurred while processing paypal payment. this should not normally happen: %s'%e, )

    logger.info('paypal payment process done')




def send_email_paypal_failed( to_, checkout_id ):
    '''
    sends email for general paypal failure
    this means the payment was not executed 
    (for whatever reason , except usage of UNVERIFIED PAYPAL account - different error)
    '''

    logger = PaymentLogger()
    logger.info('sending email. paypal payment has failed. did not execute for some reason', {'checkout_id':checkout_id, 'recipient':to_}  )
    subject='Paypal payment failed'
    basic_text_content = 'There seems to be a problem with your Paypal payment request. You may try purchasing credits using other payment options. For concerns regarding this transaction,'
    
    text_content= '%s %s' % (basic_text_content, 'please contact api@chikka.com. Thank you.')
    mailto_email='api@chikka.com'
    html_content='%s %s' % (basic_text_content, 'please contact <a href="mailto:%s">%s</a>. Thank you.' % (mailto_email, mailto_email) )
    
    try:
        __send_email( to_=to_, 
                      text_content=text_content, 
                      html_content=html_content, 
                      subject=subject
                      )

    
    except Exception, e:
        logger.error('unable to send email: %s' % e)
        
    logger.info('email has been sent')
    
    
    
    
    
    



def send_email_unverified_user_error( to_, checkout_id ):
    '''
    this function sends email to the recepient ( see params )
    regarding usage of UNVERIFIED paypal account to pay the paypal checkout
    
    '''
    
    logger = PaymentLogger()
    logger.info('sending email. paypal payment used unverified paypal account', {'checkout_id':checkout_id, 'recipient':to_}  )
    subject='Paypal payment failed'
    basic_text_content = 'There seems to be a problem with your Paypal payment request. Only verified Paypal accounts can be used for this transaction. You may try purchasing credits using other payment options. For concerns regarding this transaction,'
    
    text_content= '%s %s' % (basic_text_content, 'please contact api@chikka.com. Thank you.')
    mailto_email='api@chikka.com'
    html_content='%s %s' % (basic_text_content, 'please contact <a href="mailto:%s">%s</a>. Thank you.' % (mailto_email, mailto_email) )
    
    try:
        
        __send_email( to_=to_, 
                      text_content=text_content, 
                      html_content=html_content, 
                      subject=subject
                      )

    
    except Exception, e:
        logger.error('unable to send email: %s' % e)
        
    logger.info('email has been sent')
    

def __send_email( to_, text_content, html_content, subject  ):


    email_from_= email_sending_config['mail_from_address']
    mail_host=email_sending_config['host']
    mail_port=email_sending_config['port']


    send_mailx( text_content=text_content, 
            html_content=html_content, 
            subject=subject, 
            to_=to_, 
            email_from_=email_from_, 
            mail_host=mail_host, 
            mail_port=mail_port )




def set_failed_purchase( express_checkout_obj, logger ):
    '''
    express_checkout_obj contains the paypal token object
    
    the paypal token object contains the checkout id
    
    
    so we can load a checkout object and set that to a failed purchase
    '''
    logger.info('setting checkout and purchase records to FAILURE')
    
    try:
        checkout_id = express_checkout_obj.express_checkout_token_obj.checkout_id
        checkout_object = Checkout.get( checkout_id=checkout_id )
        
        # set checkout / purchase record to failed
        checkout_object.mark_payment_failed()
        checkout_object.status = Checkout.STATUS_FAILURE
        checkout_object.write_to_purchase_history()

    except Exception, e:
        logger.error('unable to complete setting FAILURE: %s' % e)
        
        
    else:
        
        try:
            account = Account.get( account_id = checkout_object.account_id )
            logger.info('paypal payment failed. sending email to account', {'email': account.email })
            send_email_paypal_failed( to_=account.email, checkout_id=checkout_id )
            
        except Exception, e:
            logger.error('could not send email to user')
            pass
        
        

        
def is_allowed_for_amount( amount ):
    
    is_allowed = False
    try:
        if int(amount) >= paypal_settings['min_amount_peso'] :
            is_allowed = True
    except Exception, e:
        is_allowed = False
    
    return is_allowed

def check_payment_if_success( token, checkout_id, hash ):
    '''
    checks if payment done on paypal token is successful
    
    @todo find a way to easily retrieve account id from checkout object
 
    '''
    payment_success = None
    verified_paypal = None
    
    checkout_object = Checkout.get(checkout_id=checkout_id)
    
    account_id = checkout_object.account_id
    
    
    computed_hash = get_paypal_callback_hash( account_id=account_id, checkout_id=checkout_id )
    
    if computed_hash == hash :
        
        # hash is valid, start getting info
        if checkout_object.status == checkout_object.STATUS_FAILURE:
            payment_success = False

            failed_because_unverified = PaypalToken.test_failed_by_unverified_paypal_account(checkout_id=checkout_id)
            if failed_because_unverified:
                verified_paypal = False
        
        elif checkout_object.status == checkout_object.STATUS_SUCCESS:
            payment_success = True

    return payment_success, verified_paypal


def increment_monthly_paypal_total_by( account_id, date_reference, amount ):
    print "paypalmain increment"
    
    PaypalPaymentCheckout.increment_monthly_paypal_purchase( account_id=account_id, date_reference=date_reference, amount=amount )
     
    pass


class PaypalPaymentError( Exception ):
    pass