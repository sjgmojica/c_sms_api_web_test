from gevent.monkey import patch_all
patch_all()
import gevent




import unittest
import features.registration.email as email_tool

import gredis.client

import string
import random


from models.verification import Verification
from dao.verification_email_redis import EmailVerificationRedisDAO

from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

class TestRegisterUser( unittest.TestCase ) :
    
    
    def setUp(self):
        
        
        
        
        pass


    def _test_unquoted_local_part(self):
        
        # 1 double quotes in locval part should cause failure
        
        email = 'xxx"xxx@yahoo.com'
        valid = email_tool.is_email_format_valid(email)
        self.assertFalse(valid, 'quotes are not allowed in local part of email')
        
        normal_chars = string.lowercase
        valid_special_chars = '!#$%&*+-/=?^_`{|}~'
        
        # only alphanumeric characters are allowed as first character
        for t_char in valid_special_chars :
            email = '%sabcd@domain.com' % t_char
            #print email
            valid = email_tool.is_email_format_valid(email)
            self.assertFalse(valid, '[%s] not allowed as first character'% t_char)

    def _test_name_domain_part(self):
        
        #1. only letters digits hyphen and . (period) are allowed in domain name part
        for t_char in string.punctuation :
            if t_char not in '-.':
                email = 'xyzabc@xxx%s.com' % t_char 
                valid = email_tool.is_email_format_valid(email)
                self.assertFalse(valid, '[%s] not allowed in domain name part'% t_char)
        
        # 2. only a-zA-Z 0-9 are allowed as fist char of domain name part
        for t_char in string.punctuation :
            
            email = 'xyzabc@%sxxx.com' % t_char 
            valid = email_tool.is_email_format_valid(email)
            self.assertFalse(valid, '[%s] not allowed as first char in domain name part'% t_char)
        


    def _test_email_length(self):
        
        # chikka sms api will only support emails 32 characters long
        
        email = '%s@%s.%s' %('hghghghghghghghjdjdjdjdjdd', 'jdjdjdjdjdjdjdjdsaqeeqq', 'dddddd')
        valid = email_tool.is_email_format_valid(email)
        self.assertFalse(valid, 'email should only be at max 32 characters long')
        
    
    def test_push_email_to_queue(self):
        '''
        test if emails are pushed to the queue in FIFO manner 
        '''
        
        for x in range( 3 ):
            Verification.add_email_to_reg_queue( email='kirby@kirby-agudelo%s.net'%x )
        
        
if __name__ == '__main__':
    
    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()

    Verification.cache_dao
        
    redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
    redisconn.connect()
    print redisconn
    Verification.cache_dao = EmailVerificationRedisDAO( redis_conn=redisconn )

    

    
    unittest.main( verbosity=2 )