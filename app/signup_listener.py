from gevent.monkey import patch_all
patch_all()

import gredis.client
from tornado.options import define, options, parse_command_line, print_help

from utils.send_mailx import send_mailx
from utils.sql_tools import SQLUtils
from features.configuration import Configuration



from dao.account_mysql import AccountMySQLDAO
from models.account import Account

define("config", default='debug', help="run configuration settings", type=str) 
define("local_settings", default="true", help="enable/disable use of local settings", type=str)



parse_command_line()
Configuration.initialize()

values = Configuration.values()


redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
redisconn.connect()


dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
        port=values['mysql-db']['sms_api_config']['port'],
        database=values['mysql-db']['sms_api_config']['db'],
        user=values['mysql-db']['sms_api_config']['user'],
        password=values['mysql-db']['sms_api_config']['password'])

Account.dao = AccountMySQLDAO( sql_util=dbconn )


email_queue_key = 'smsapi_signup_email_queue'
email_queue_key = 'testlist'

while True :


    try :
        result = redisconn.brpop( email_queue_key )

        if len( result ) == 2 :
            
            print 'send to ', result[1] 

    except Exception, e:
        
        pass