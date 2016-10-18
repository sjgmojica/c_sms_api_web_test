'''
initialization for paymaya module

'''
from tornado.options import options
from utils.sql_tools import SQLUtils

if options.config =='prod':
    config_mode = 'prod'
elif options.config =='staging':
    config_mode = 'stg'
else:
    config_mode = 'debug'

import gredis.client

#from features.configuration import Configuration
from ..configuration import Configuration
print 'config imported'
all_configs = Configuration.values()
paymaya_settings = all_configs['paymaya']


mysql_cfg = Configuration.values()['mysql-db']['sms_api_config']

sql_util = SQLUtils(host=mysql_cfg['host'],
            port=mysql_cfg['port'],
            database=mysql_cfg['db'],
            user=mysql_cfg['user'],
            password=mysql_cfg['password']) 
