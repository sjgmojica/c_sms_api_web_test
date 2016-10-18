import unittest


from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration
parse_command_line()


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


Configuration.initialize()

values = Configuration.values()



from models.account import Account
from models.checkout import Checkout
import features.payments.notification as payment_notif_tool


class TestNotifyFromPayment( unittest.TestCase ) :
    
    
    def setUp(self):
        pass
    
    def test_send_email_payment_notification(self):
        
        account_object = Account.get( account_id = 4 )
        checkout_object = Checkout.get( checkout_id=329 )
        
        print 'email!!!'
        
        
        payment_notif_tool.notify_payment_successful( checkout_object=checkout_object, account_object=account_object )
        #body = payment_notif_tool.prepare_payment_notif_body( amount=1000, current_balance=1234 )
        #print body
        
if __name__ == '__main__':
    

    
    unittest.main( verbosity=2 )