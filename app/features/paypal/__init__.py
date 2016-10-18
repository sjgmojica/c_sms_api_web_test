'''
initialization for paypal module

'''
from tornado.options import options

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
cfg_values = Configuration.values()    
# ----------------------------------------


from utils.sql_tools import SQLUtils



from dao_interface import DummyDao
from dao.paypal_mysql import PaypalMysqlDAO
from .paypal_purchase_history_mysql_dao import PaypalPurchaseHistoryMysqlDAO




from .paypal_token_model import PaypalToken 
from .paypal_dao_cache import PaypalRedisDao



from .paypal_checkout_model import PaypalPaymentCheckout



redis_cfg = cfg_values['redis_servers']['sms_api']
redisconn = gredis.client.Connection(address=str(redis_cfg['host']), port=int(redis_cfg['port']))
redisconn.connect()


all_configs = Configuration.values()

paypal_settings = all_configs['paypal']

email_sending_config = all_configs['mailer']

api_version =  paypal_settings['api_version']

api_merchant_user = paypal_settings['merchant_user']
api_merchant_paassword = paypal_settings['merchant_paassword']
api_merchant_signature = paypal_settings['merchant_signature']
api_endpoint_url = paypal_settings['api_endpoint_url']

# in prod, use www.paypal.com
paypal_website_domain = paypal_settings['paypal_website_domain'] #   'www.sandbox.paypal.com'

# used to point to website and say that transaction is now underway (after checkout)
website_callback_url = paypal_settings['website_base_url'] #'http://10.11.2.225:28003'


# get the maximum amount an account can purchase per month using paypal
max_purchase_value_per_month = paypal_settings['max_purchase_value_per_month']

# setup the paypal mysql dao
# must implement the dao interface

mysql_cfg = Configuration.values()['mysql-db']['sms_api_config']

sql_util = SQLUtils(host=mysql_cfg['host'],
            port=mysql_cfg['port'],
            database=mysql_cfg['db'],
            user=mysql_cfg['user'],
            password=mysql_cfg['password']) 


mysql_dao = PaypalMysqlDAO( sql_util=sql_util )
PaypalToken.db_util = mysql_dao 




PaypalToken.cache_dao = PaypalPaymentCheckout.paypal_cache_dao = PaypalRedisDao(redisconn=redisconn, config_mode=config_mode, paypal_pending_payment_flag_ttl=paypal_settings['purchase_waiting_time'])

PaypalPaymentCheckout.purchase_history_dao = PaypalPurchaseHistoryMysqlDAO( sql_util=sql_util )

 