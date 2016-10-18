'''
contains features regarding notification upon payment





'''

from datetime import datetime
import utils.add_sms_credits as credit_tool
from utils.text_api import send_generic_sms
from utils.generic_mailer import send_generic_mail
import features.logging as sms_api_logger

def notify_payment_successful( account_object, checkout_object, send_sms=True):
    '''
    this function sends notification to the user regarding successful credit top up
    for now, email and sms are sent  
    requires a valid account object
    
    '''
    l = sms_api_logger.PaymentLogger()


    current_date_formatted = datetime.now().strftime('%b %d, %Y %H:%M')
    
    try:
        amount = float(checkout_object.amount)
        current_balance = float(credit_tool.get_balance( account_object.suffix ))
    except:
        amount = 0
        current_balance = 0
    
    l.info( 'sending_notification',  {'amount_paid':checkout_object.amount, 'account id': account_object.account_id, 'checkout id': checkout_object.checkout_id }  )
    
    l.info('notifying user by email', {'email':account_object.email})
    
    body = prepare_payment_notif_body( amount=amount, current_balance=current_balance   )
    __queue_email_notification( email=account_object.email, body=body )
    
    if send_sms:
        l.info('notifying user via sms', { 'phone': checkout_object.phone})
        sms_body ='%s This msg is free' % body 
    
    __send_sms_notif( phone=checkout_object.phone, body=sms_body )


def prepare_payment_notif_body( amount, current_balance   ):
    '''
    function for generating the body of the email / sms message
    this is also useful for testing the spiel
    '''
    current_date_formatted = datetime.now().strftime('%b %d, %Y %H:%M')
    contact_details = 'api@chikka.com'
    
    amount_formatted = 'P%s'%  format( amount, ',.2f' )
    balance_formatted = 'P%s'%  format( current_balance, ',.2f' )
    
    
    body = """You have successfully purchased %s worth of credits. You were charged %s for this transaction. Your total credits as of %s is %s. 

For concerns regarding this transaction, please contact: %s.""" % ( amount_formatted, amount_formatted, current_date_formatted, balance_formatted , contact_details)
    
    return body


def __queue_email_notification( email, body ):
    
    
    send_generic_mail(email, ' Your payment  notification', body, mail_from='developers@chikka.com' )
     
    

def __send_sms_notif( phone, body ):
    send_generic_sms( phone=phone, body=body )
    
    
    # utils/text_api.py
    #gawa na lang po kayo ng version nyo po ng send_pincode()