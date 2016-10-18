'''
    @author: Jhesed Tacadena
    @date: 2013-12
    @description:
        - tests if fluent logging is working properly for
        standalone applications
'''

import features.logging as sms_api_logger
from datetime import datetime

def start_test():
    
    print 'started logging test...'
        
    email_logger = sms_api_logger.StandAloneEmailNotifierLogger() 
    email_logger.info('-- Test Log for Email Notifiers --', {'date': datetime.now()})
    
    su_logger = sms_api_logger.StandAloneSuffixFreeToInactiveLogger()    
    su_logger.info('-- Test Log for Free To Inactive Updater --', {'date': datetime.now()})
                        
    su_logger = sms_api_logger.StandAloneSuffixPaidToInactiveLogger()     
    su_logger.info('-- Test Log for Paid To Inactive Updater --', {'date': datetime.now()})
    
    su_logger = sms_api_logger.StandAloneSuffixUnpaidToInactiveLogger()  
    su_logger.info('-- Test Log for Unpaid To Inactive Updater --', {'date': datetime.now()})
        
    print 'finished logging test'
    
start_test()