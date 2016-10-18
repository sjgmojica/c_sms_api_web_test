'''
initialize wpp-wide models (models used globally regardless of app

'''
import gredis.client
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

from .account import Account
from .session import Session
from .checkout import Checkout
from .verification import Verification
from .transaction_history import TransactionHistory

from .shopping_cached_cart import ShoppingCachedCart
from .suffixes import Suffixes

from .packages import Packages
from .shopping_cart import ShoppingCart

from .content_providers import ContentProviders
from .dragonpay import Dragonpay
from .lock_cache import LockCache

from dao.account_mysql import AccountMySQLDAO
from dao.account_redis import AccountCacheDAO
from dao.verification_email_redis import EmailVerificationRedisDAO
from dao.verification import VerificationDao
from dao.session_redis import SessionRedisDAO
from dao.checkout_mysql import CheckoutMysqlDAO
from dao.purchase_history_mysql import PurchaseHistoryMysqlDAO
from dao.transaction_history import TransactionHistoryMySQL
from dao.shopping_cached_cart import ShoppingCachedCartDao
from dao.packages import PackagesDao
from dao.shopping_cart import ShoppingCartDao
from dao.content_providers import ContentProvidersDao
from dao.suffixes import SuffixesDao
from dao.dragonpay import DragonpayDao
from dao.lock_cache import LockCacheDao

from utils.sql_tools import SQLUtils
from features.configuration import Configuration
import features.logging as sms_api_logger
from datetime import timedelta
from tornado.options import parse_command_line, options

values = Configuration.values()    

mysql_cfg = values['mysql-db']['sms_api_config']

dbconn = SQLUtils(host=mysql_cfg['host'],
            port=mysql_cfg['port'],
            database=mysql_cfg['db'],
            user=mysql_cfg['user'],
            password=mysql_cfg['password'])    


redis_cfg = values['redis_servers']['sms_api']


redisconn = gredis.client.Connection(address=str(redis_cfg['host']), port=int(redis_cfg['port']))
redisconn.connect()


Account.dao = AccountMySQLDAO( sql_util=dbconn )
Account.cache_dao = AccountCacheDAO( redis_conn=redisconn )
    

Suffixes.dao = SuffixesDao(dbconn=dbconn)

Packages.dao = PackagesDao(dbconn=dbconn)


ContentProviders.dao = ContentProvidersDao(dbconn=dbconn, redisconn=redisconn)  # ! temp ! change redis host port

Verification.dao = VerificationDao( dbconn=dbconn, redisconn=redisconn )
Verification.cache_dao = EmailVerificationRedisDAO( redis_conn=redisconn )
Verification.cache_dao.signup_email_queue_key = values['verify_email_queue_key']    



Verification.signup_verify_expiration_length = timedelta( hours=48 )
Verification.change_email_verify_expiration_length = timedelta( hours=48 )


Verification.verification_base_url = values['website_base_url']

Session.cache_dao = SessionRedisDAO( redis_conn=redisconn )

Checkout.db_dao = CheckoutMysqlDAO( sql_util=dbconn )
Checkout.purchase_history_dao = PurchaseHistoryMysqlDAO( sql_util=dbconn )

TransactionHistory.dao = TransactionHistoryMySQL( sql_tool=dbconn )

ShoppingCart.dao = ShoppingCartDao(dbconn=dbconn) 
ShoppingCachedCart.dao = ShoppingCachedCartDao(redisconn=redisconn)
ShoppingCachedCart.dao.CHECKOUT_QUEUE_KEY = values['checkout_queue_key']
  
parse_command_line()

if options.config == 'prod':
    url = URL('https://%s' %values['dragonpay']['host'])
else:
    url = URL('http://%s' %values['dragonpay']['host'])

Dragonpay.dao = DragonpayDao(dbconn=dbconn)
Dragonpay.http_conn = HTTPClient.from_url(url, concurrency=10) 

LockCache.dao = LockCacheDao(conn=redisconn, logger=sms_api_logger.PaymentLogger())
