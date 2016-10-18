'''
these are the main components of the balance notification

'''
from functools import wraps


from utils.send_mailx import send_mailx
from utils.add_sms_credits import get_zero_credit_date


from models.account import Account, AccountSaveException

from . import mailer_host, mailer_port

from datetime import datetime, timedelta

shortcode_prefix=29290
shortcode_expiry_for_paied = 90 # days


minimum_threshold = 50
maximum_threshold = 100000

from gevent.pool import Pool

job_pool = Pool( 10 )

def inspect_balance_for_notif( client_id, suffix ):
    '''
    this inspects an account's balance and checks if it is zero (absolute) or just below balance threshold
    
    
    '''
    # get account info using suffix and make sure the client id belongs to that user
    account_object = Account.get( suffix=suffix )
    
    if account_object and \
        account_object.package_type == Account.PACKAGE_PAID and \
        account_object.balance_notif_enabled and \
        account_object.client_id == client_id :

        current_balance = account_object.balance
        
        balance_threshold = account_object.balance_notif_threshold
        email = account_object.email
        
        current_datetime = datetime.now()
        
        if current_balance == 0 and not account_object.get_zero_balance_notif_sent():
            # send zero balance email
            # if balance is == 0

            #--- --------------------------------------------
            zero_balance_date = get_zero_credit_date( suffix=suffix )
            expiry_date = zero_balance_date + timedelta( days=shortcode_expiry_for_paied )
            #--- --------------------------------------------
            
            send_zero_credit_notif( email=email, shortcode='%s%s'%(shortcode_prefix, suffix ), expiry_date=expiry_date )
            
            # sent notif sent
            account_object.set_zero_balance_notif_sent()
            

        elif current_balance <= balance_threshold  and not account_object.get_balance_threshold_notif_sent():
            send_balance_threshold_notif( email=email, balance=current_balance, threshold=balance_threshold, date_notif=current_datetime )
            
            # mark notification as sent
            account_object.set_balance_threshold_notif_sent() 
            
        else:
            print 'balance is ok', current_balance
             
    else:
        # no account exists or
        # balance notif not enabled or
        # suffix is not for client id or no account 
        print 'ignore accounts'




def validBalanceNotifInput(f):
    
    @wraps(f)
    def wrapper( *args, **kwargs ):
        
        print 'calling function'
        # check if account_object is in proper format (Account type)
        

        if args :
            account_object = args[0]
        else:
            account_object = kwargs['account_object']
        
        if Account is not type(account_object):
            raise BalanceNotificationModuleError( 'enable_balance_notif() accepts Account object, %s given' % type(account_object) )

        return f( *args, **kwargs )
    
    return wrapper
    

@validBalanceNotifInput
def enable_balance_notification( account_object ):
    '''
    this function enables and sets the threshold value for a user
    business rules are applied here such as
    minimum threshold value and maximum threshold value
    
    '''
    
    

    try:
        # execute set/update balance notif
        account_object.enable_balance_notification( )

    except AccountSaveException, e :
        '''
        only expected exception, which means the account data could not be save 
        '''
        raise BalanceThresholdSaveException('unable to enable/set balance notification: %s' % e)


@validBalanceNotifInput
def disable_balance_notification( account_object ):
    '''
    disables the balance notification
    
    '''
    try :
        account_object.disable_balance_notification()
    except AccountSaveException, e :
        raise BalanceThresholdSaveException('unable to disable balance threshold notification: %s' % e)

@validBalanceNotifInput
def update_balance_threshold( account_object, threshold ):
    
    
    try:
        threshold = int(threshold)
    except Exception, e:
        raise InvalidThresholdAmountError('invalid threshold amount: [%s] : %s' % (threshold, e)  )
 
    if threshold < minimum_threshold or threshold >  maximum_threshold :
        raise InvalidThresholdAmountError('invalid threshold: [%s] : enter any value above %s but below %s' % (threshold, minimum_threshold,maximum_threshold )  )


    account_object.balance_notif_threshold = threshold
    account_object.set_balance_threshold()
    
    try:
        # reset flags less critical
        # balance threshold sent
        account_object.reset_zero_balance_notif_sent()
        # zero balance threshold sent
        account_object.reset_balance_threshold_notif_sent()
    except:
        pass

def send_balance_threshold_notif( email, balance, threshold, date_notif ):
    
    
    subject='Threshold reached notification'

    
    threshold_formatted = 'P%s'%  format( threshold, ',.2f' ) 
    date_formatted = date_notif.strftime('%B %d %Y; %I:%M %p').replace(' 0', ' ')
    balance_formatted = 'P%s'%  format( balance, ',.2f' ) 
    

    html_content = """Hi Partner,<br>
<br>We've noticed that your Chikka API balance has reached %s as of %s. 
You may choose to top up your balance <a href="https://api.chikka.com/cart">here</a>.<br><br>
Your current threshold limit is set to %s. You may choose to modify this anytime in <a href="https://api.chikka.com/account/settings/view">Account Settings</a>. 
""" % ( balance_formatted, date_formatted , threshold_formatted )
    
    
    job_pool.spawn( __send_notification_email, email=email, subject=subject, html_content=html_content  )
    #__send_notification_email( email=email, subject=subject, html_content=html_content  )
    
    


def send_zero_credit_notif( email, shortcode, expiry_date ):
    
    
    
    expiry_date_formatted =  expiry_date.strftime('%B %d %Y').replace(' 0', ' ')  #September 3, 2014'
    
    subject='threshold notification'
    html_content = """Hi Partner,<br><br>
We've noticed that you have insufficient balance on your Chikka API account. Please be reminded that your short code %s will expire in 90 days (%s). We are encouraging you to top up in order to keep your short code. Please see expiry rules - https://api.chikka.com/help#expiry
<br><br>
You may choose to top up your balance here  - https://api.chikka.com/account/settings/view""" % (shortcode, expiry_date_formatted)
    
    
    
    job_pool.spawn( __send_notification_email, email=email, subject=subject, html_content=html_content  )
    


def __send_notification_email( email, subject, html_content, text_content='' ):
    


    if not text_content:
        text_content = 'text content'


    email_content='email content'
    mail_from='chikkadev@chikka.com'
    
    send_mailx(
           text_content=email_content, 
           html_content=html_content, 
           subject= subject , 
           to_=email,
             
           email_from_ = 'noreply_api@chikka.com',
           mail_host=mailer_host, 
           mail_port=mailer_port
           )


class BalanceNotificationModuleError( Exception ):
    pass



class InvalidThresholdAmountError( BalanceNotificationModuleError ):
    pass

class BalanceThresholdSaveException( BalanceNotificationModuleError ):
    pass