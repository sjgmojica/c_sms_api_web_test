
from balance_notification_model import BalanceNotification

import gevent
import features.logging as chikka_sms_api_logger
from models.account import Account 


def notif_process():
    
    
    
    # recover items from queue
    # loop each item in bckup queue
    print 'start flush'
    while True:
        print 'step'
        # flushes out backup queue until empty
        popped_value = BalanceNotification.pop_balance_backup_notif()
        if not popped_value:
            break

    # start regular loop
    while True :
        l = chikka_sms_api_logger.GeneralLogger()
        
        popped_value = BalanceNotification.pop_balance_notif()
        l.info('received item for notification' , {'suffix': popped_value})
        process_suffix_balance_notification( popped_value, l  )
        
        # remove popped value from backup queue
        BalanceNotification.pop_out_backup_queue()
        gevent.sleep(5)
    
def process_suffix_balance_notification( suffix, logger ):
    
    logger.info('proccessing for suffix', {'suffix': suffix})
    
    # step 1 get account that owns suffix
    
    account = Account.get( suffix=suffix )
    if account:
        print 'account loaded'
        
        
        print 'checking balance'
        print 'balance is %s' % account.balance
        
        
        # if balance is less than 
        

    else:
        
        logger.error('no account has that suffix', {'suffix': suffix})
        
    
    
    logger.info('process done', {'suffix': suffix})