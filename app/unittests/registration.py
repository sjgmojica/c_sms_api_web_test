from tornado.options import define, parse_command_line
from features.configuration import Configuration

import gevent
import gredis.client

import unittest

from models.account import *
from utils.sql_tools import SQLUtils


from dao.account_mysql import AccountMySQLDAO

from features.registration.registration import register_user 
from features.registration.email_verification import verify_signup_email

from dao.verification import VerificationDao

from models.verification import Verification
from dao.verification_email_redis import EmailVerificationRedisDAO
from datetime import datetime, timedelta

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)




class TestRegisterUser( unittest.TestCase ) :
    
    
    def setUp(self):
        
        
        mysql_tool = SQLUtils( host='10.11.2.225',port=3306,
                            database='sms_api',user='root',password='')
        
        Account.dao = AccountMySQLDAO( sql_util=mysql_tool )
        
        
        
    def test_enter_details(self):
        '''
        test register a pending user
        CHANGE FUNCTION NAME TO test_enter_details() TO TEST
        
        
        '''
        register_user(first_name = None, 
                  last_name=None, 
                  email='kirby%s@agudelo.net' % datetime.now().strftime('%s'), 
                  company_name=None, 
                  address=None, 
                  password='aaaaaaaaaaaa'
                  )
    

            
    def __test_create_verified_account(self):
        
        
        # step 1 create pending account
        
  
        # step 2 verifiy pending account
        #Verification.verify_account( code='ba6005189c5463d02bedbaf1e2d929f8')
        verify_signup_email( code='ba6005189c5463d02bedbaf1e2d929f8' )
        
        
        
if __name__ == '__main__':
    
    parse_command_line()
    Configuration.initialize()

    
    values = Configuration.values()

    dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
        port=values['mysql-db']['sms_api_config']['port'],
        database=values['mysql-db']['sms_api_config']['db'],
        user=values['mysql-db']['sms_api_config']['user'],
        password=values['mysql-db']['sms_api_config']['password'])


    #Verification.cache_dao
    
    
    
    redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
    redisconn.connect()
    Verification.dao = VerificationDao( dbconn=dbconn ) 
    Verification.cache_dao = EmailVerificationRedisDAO( redis_conn=redisconn )
    Verification.signup_verify_expiration_length = timedelta( hours=48 )
    Verification.verification_base_url = values['website_base_url']
    
    
    unittest.main( verbosity=2 )