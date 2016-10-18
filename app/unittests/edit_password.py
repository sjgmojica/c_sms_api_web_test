import unittest
import string

import random
from tornado.options import define, options, parse_command_line
define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


from features.configuration import Configuration
Configuration.initialize()




from features.account_management import password as edit_passwsord_tool
from features.registration import password as reg_password_tool
from models.account import Account  


class TestEditPassword( unittest.TestCase ) :
    
    
    test_user_account_id = 79
    
    def setUp(self):
        
        print 'start test'
        
    def test_invalid_old_password(self):
        
        
        old_password = '12345678aaa'
        new_password = '87654321'
        
        #edit_passwsord_tool.edit_password( self.test_user_account_id, old_password, new_password )
        
        
        
        self.assertRaises( edit_passwsord_tool.InvalidOldPassword , edit_passwsord_tool.edit_password, self.test_user_account_id, old_password, new_password)
        
        
        
    def test_invalid_new_password_length(self):
        '''
        test if exception is raised on invalid new password length
        '''
        
        old_password = '12345678aaa'
        new_password = '123'
        
        self.assertRaises( reg_password_tool.InvalidPasswordLength , edit_passwsord_tool.edit_password, self.test_user_account_id, old_password, new_password)

    def test_invalid_password_format(self):
        '''
        check if password contains invalid characters
        valid characters are only:
          
        '''
        
        old_password = '12345678aaa'
        new_password = '1233232323232323%$%$#%#%'
        
        #self.assertRaises( reg_password_tool.InvalidPasswordFormat , edit_passwsord_tool.edit_password, self.test_user_account_id, old_password, new_password)
        self.assertRaises( reg_password_tool.InvalidPasswordFormat , edit_passwsord_tool.edit_password, self.test_user_account_id, old_password, new_password)
        
    
    def test_save_correcrt_password(self):
        '''
        save a valid new password and compares password
        
        '''
        old_password = '12345678'
        
        
        valid_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        valid_length = {'min':8, 'max':32}
        
        # generate random new password
        new_password = ''.join(random.choice( valid_characters ) for x in range(  valid_length['min'], valid_length['max']  ) )
        
        
        result = edit_passwsord_tool.edit_password( self.test_user_account_id, old_password, new_password )
        
        self.assertTrue(result, 'could not save new password')
        
        # compare with new password if it was really saved
        account_object = Account.get( account_id = self.test_user_account_id )
        
        is_same_as_current_password = account_object.check_same_old_password(  reg_password_tool.encrypt(new_password) )
        self.assertTrue(is_same_as_current_password, 'password is not same as saved')
        
        # return old password
        result = edit_passwsord_tool.edit_password( self.test_user_account_id, new_password, old_password )
        self.assertTrue(is_same_as_current_password, 'could not return to original password')
    
        


if __name__ == '__main__':
    
    
    
    unittest.main( verbosity=2 )
    