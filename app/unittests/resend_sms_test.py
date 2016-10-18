'''
unit test for send sms

usage

set path to the root of application

i.e.
export PYTHONPATH=/home/kirby/Source/sms_api/2014-08-11_sprint4_resend_sms

execute while in appliction root

python unittests/resend_sms_test.py


load up dummy values to be used

@author: vincent agudelo

'''


import unittest
import string

from tornado.options import define, options, parse_command_line
define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


from features.configuration import Configuration
Configuration.initialize()


from features.payments.resend_pin_code import resend_sms, CheckoutNotExistError, \
NonPendingCheckoutResendSmsError, ResendNotSupported, MaxResendReachedError, ResendTimeLimitReached



non_existing_checkout_id=1
#expired_checkout_id =
non_pending_checkout_id = 7 


non_smart_payment_checkout = 68

expired_checkout = 218


resend_maxed_out_checkout = 215 

resend_timeout_reached_checkout = 198




class TestResendSms( unittest.TestCase ) :
    
    def setUp(self):
        
        pass
        
    def tearDown(self):
        pass
        


    #--- the tests

    def test_invalid_id(self):
        
        self.assertRaises( CheckoutNotExistError, resend_sms,  checkout_id = 'hdhfhfsdf\'\'\'\'\\'  )


    def test_non_existing_checkout(self):
        '''
        checks result if resend sms is run using non-existing checkout
        '''
        
        self.assertRaises( CheckoutNotExistError, resend_sms,  checkout_id = non_existing_checkout_id  )


    def test_non_null_status_checkout(self):
        '''
        only pending checkout can resend sms
        exception should be rasied if resend sms happened on non-pending checkout. should not happen
        '''
        
        self.assertRaises( NonPendingCheckoutResendSmsError, resend_sms,  checkout_id = non_pending_checkout_id  )
        
 
    def test_maxed_out_rersend_ctr(self):
        '''
        test if checkout has maxed out resend ctr
        '''
        
        self.assertRaises( MaxResendReachedError, resend_sms,  checkout_id = resend_maxed_out_checkout  )
        
        
        
 
    def test_expired_checkoout(self):
        '''
        test expired checkout
        '''
        
        self.assertRaises( ResendNotSupported, resend_sms,  checkout_id = expired_checkout  )
        
 
    def test_resend_time_limit(self):
        '''
        test a checkout (non expired) that has reached time limit for resend
        
        '''
        
        
        self.assertRaises( ResendTimeLimitReached, resend_sms,  checkout_id = resend_timeout_reached_checkout  ) 
        




if __name__ == '__main__':
    #unittest.main( verbosity=2 )
    
    
    resend_sms( checkout_id=283 )