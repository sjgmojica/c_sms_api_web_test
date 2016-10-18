import unittest
import string

import random


from features.login import login


class TestRegisterUser( unittest.TestCase ) :
    
    def setUp(self):
    
        pass
    
    
    def __test_login_with_invalid_email_format(self):
        
        char_list = string.punctuation
        char_list='%s '%char_list
        for t_char in char_list:
            
            email='%sxxxyyy%s@yah%soo.com'% (t_char,t_char,t_char)
            success = login(email=email , password='12345678')
            self.assertFalse(success, 'login with invalid email not allowed')
            
        # test using utf-8 special characters
        
        email = 'ccc\xc3\x8b@yahoo.com'
        
        success = login(email=email , password='12345678')
        self.assertFalse(success, 'login with invalid email not allowed')
        
        # test using unicode
        
        email = 'cc%s@yahoo.com' % unichr(40960)
        
        success = login(email=email , password='12345678')
        self.assertFalse(success, 'login with invalid email not allowed')
        
        # testing unicode with NORMAL EMAIL
        email = u'kirby@kirby-agudelo.net'
        
        success = login(email=email , password='12345678')
        self.assertTrue(success, 'login with invalid email not allowed')
        

    def test_login_with_invalid_password_format(self):
        
        # with invalid characters
        char_list = string.punctuation
        char_list='%s '%char_list
        for t_char in char_list:
            
            password = '123%sffgg55' % t_char 
            success = login(email='kirby@kirby-agudelo.net' , password=password)
            self.assertFalse(success, 'login with invalid password not allowed')

        # with utf8 characters
        
        password = 'dddddddddd \xc3\x8b ddddd'
        success = login(email='kirby@kirby-agudelo.net' , password=password)
        self.assertFalse(success, 'login with invalid password not allowed')
        
        # unicode characters
        password = u'dddddddddd \xcb ddddd'
        success = login(email='kirby@kirby-agudelo.net' , password=password)
        self.assertFalse(success, 'login with invalid password not allowed')
        
        
        #using unicode with correct format text
        password = u'dddddddddd454232ddddd'
        success = login(email='kirby@kirby-agudelo.net' , password=password)
        self.assertTrue(success, 'login with invalid password not allowed')
        
        
        
        
if __name__ == '__main__':
    unittest.main( verbosity=2 )