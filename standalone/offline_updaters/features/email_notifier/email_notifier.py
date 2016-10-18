'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
        - sends email notifications to accounts 
        with expiring suffixes:        
            + package=FREE, 7 days before expiration
            + package=PAID, 30 days before expiration
            + package=PAID, 14 days before expiration 
'''

from base_email_notifier import BaseEmailNotifier
import features.logging as sms_api_logger
from datetime import datetime

CC_EMAILS = [
    'rrivera@chikka.com',
    'vagudelo@chikka.com',
    'mrgiaquino@chikka.com',
    'jdtacadena@chikka.com'
]


class EmailNotifier(object):

    def main(self):
        '''
            @description:
                - encapsulates the whole free
                suffix updating process
        '''
        ben = BaseEmailNotifier()
        ben.init()  # initializes base conns and configs
        
        # --- email for package == FREE ---
        
        print '\n - starting EMAIL NOTIFS for FREE package - \n'
        
        free_expire_in_7days_details = self.__email_free_account(ben)
        # self.__print_debug_suffix_info()
        
        # --- email for package == PAID ---
        
        print '\n - starting EMAIL NOTIFS for PAID package - \n'
        
        (paid_expire_in_30days_details, paid_expire_in_14days_details) = \
            self.__email_paid_account(ben)
        
        # self.__print_debug_suffix_info()
       

       # send confirmation email to chikka sms api admins
       # that users were successfully warned that their
       # suffix is about to expire
        self.send_confirmation_email(ben, CC_EMAILS, 
            free_expire_in_7days_details, paid_expire_in_30days_details,
            paid_expire_in_14days_details)
       
    def __email_free_account(self, base_email_notifier_instance):
        '''
            @description:        
                # days_interval = 1 week before expiration
                # 30 days - 7 days        
        '''
        
        email_logger = sms_api_logger.StandAloneEmailNotifierLogger() 
        email_logger.info('START processing FREE accounts')
    
        suffixes_info = base_email_notifier_instance.select_suffix(
            days_interval=23, status='ACTIVE', package='FREE')
        
        if suffixes_info:
            for si in suffixes_info:
                base_email_notifier_instance.send_email(
                    to_address=si['email'], shortcode=si['suffix'],
                    days_before_expiration='Seven')
       
                email_logger.info('FREE: now sending email -- 7 days before expiration', 
                    {'email': si['email'], 'shortcode': si['suffix'], 'date': datetime.now()})
        
        email_logger.info('END processing FREE accounts')        
        return suffixes_info
        
    def __email_paid_account(self, base_email_notifier_instance):
        '''
            @description:        
                # days_interval = 30 days before expiration
                # 90 days - 30 days        
                
                # AND
                
                # days_interval = 14 days before expiration
                # 90 days - 14 days        
        '''
        
        email_logger = sms_api_logger.StandAloneEmailNotifierLogger() 
        email_logger.info('START processing PAID accounts')
        
        # email user 30 days before expiration
        
        suffixes_info30 = base_email_notifier_instance.select_suffix(
            days_interval=60, status='ACTIVE', package='PAID')
        
        if suffixes_info30:
            for si in suffixes_info30:
            
                    
                if base_email_notifier_instance.is_paid_suffix_expiring(
                    grace_period_in_days=90,
                    suffix=si['suffix']):
                
                    base_email_notifier_instance.send_email(
                        to_address=si['email'], shortcode=si['suffix'],
                        days_before_expiration='Thirty')
                        
                    email_logger.info('PAID: now sending email -- 30 days before expiration', 
                        {'email': si['email'], 'shortcode': si['suffix']})
                                    
        # email user 14 days before expiration
        
        suffixes_info14 = base_email_notifier_instance.select_suffix(
            days_interval=76, status='ACTIVE', package='PAID')
        
        if suffixes_info14:
            for si in suffixes_info14:
            
                
                if base_email_notifier_instance.is_paid_suffix_expiring(
                    grace_period_in_days=90,
                    suffix=si['suffix']):

                    base_email_notifier_instance.send_email(
                        to_address=si['email'], shortcode=si['suffix'],
                        days_before_expiration='Fourteen')
        
                    email_logger.info('PAID: now sending email -- 14 days before expiration', 
                        {'email': si['email'], 'shortcode': si['suffix']})
                
        email_logger.info('END processing PAID accounts')
        # returns tuple of the details
        return (suffixes_info30, suffixes_info14)
        
    # def __print_debug_suffix_info(self):
        # print '\nfree suffixes dict: ' 
        # print suffixes_info
  
    def send_confirmation_email(self, base_email_notifier_instance, 
        cc_emails, free_details, paid30_details, paid14_details):
        '''
            @description:
                - sends confirmation email to chikka sms api admin
                that all accounts that will expire within x days 
                have successfully been sent a warning message
            @param free_details:
                - package=FREE, 7 days before expiration
            @param paid30_details:
                - package=PAID, 30 days before expiration
            @param paid14_details:
                - package=PAID, 14 days before expiration
        
        '''
        for ce in cc_emails:    
            base_email_notifier_instance.send_confirmation_email(
                to_address=ce, free_details=free_details,
                paid30_details=paid30_details,
                paid14_details=paid14_details)
    
    

          
def start_email_notifiers():
    '''
        @description:
            - 
    '''
    en = EmailNotifier()
    en.main()

