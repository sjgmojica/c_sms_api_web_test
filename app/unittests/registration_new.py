import unittest


from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration
parse_command_line()


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

Configuration.initialize()

values = Configuration.values()



from models.account import Account


from features.registration import registration as registration_tool


class TestRegisterNew( unittest.TestCase ) :
    
    
    active_account_email = 'rrivera@chikka.com'
    pending_account_email = 'sss@qqq'
    
    def setUp(self):
        pass
    
    def test_register_existing_active(self):
        
        
            
        self.assertRaises(registration_tool.ActiveAccountAlreadyExisting, 
                              registration_tool.register_user,
                              first_name='', last_name='', 
                                         email=self.active_account_email, 
                                         company_name='', 
                                         address='', 
                                         password='12345678', 
                                         password_again='12345678'
                              )
            
        
    
        
if __name__ == '__main__':
    

    
    unittest.main( verbosity=2 )