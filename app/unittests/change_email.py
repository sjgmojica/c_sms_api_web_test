from gevent.monkey import patch_all
patch_all()
import gevent

import unittest


import gredis.client

from models.verification import Verification, InvalidVerifyCodeFormat
from dao.verification_email_redis import EmailVerificationRedisDAO
from dao.verification import VerificationDao


from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration

from utils.sql_tools import SQLUtils

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

class TestRegisterUser( unittest.TestCase ) :
    def setUp(self):
        pass
    
    
    def test_verify_change_email( self ):

        invalid_long_code = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        #invalid_long_code = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        
        self.assertRaises( InvalidVerifyCodeFormat, Verification.get_change_email_verification_by_code,  code=invalid_long_code )
        
        #invalid_long_code = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        invalid_long_code = 'aaaa%%$#%$^aaaaddddaaaaqaaaaaaaa'
        self.assertRaises( InvalidVerifyCodeFormat, Verification.get_change_email_verification_by_code,  code=invalid_long_code )
        
        

    def test_valid_code(self):
        
        
        invalid_long_code = 'c70a4ef428ca65ee0d8b23fd3a33bf1b'
        Verification.get( code=invalid_long_code )
        
        
if __name__ == '__main__':


    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()


    dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
        port=values['mysql-db']['sms_api_config']['port'],
        database=values['mysql-db']['sms_api_config']['db'],
        user=values['mysql-db']['sms_api_config']['user'],
        password=values['mysql-db']['sms_api_config']['password'])


    Verification.cache_dao
    Verification.dao = VerificationDao( dbconn=dbconn )
        
    redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
    redisconn.connect()
    print redisconn
    Verification.cache_dao = EmailVerificationRedisDAO( redis_conn=redisconn )

    

    
    unittest.main( verbosity=2 )