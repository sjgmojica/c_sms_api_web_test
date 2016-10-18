#setup dao


# mysql dao

# for this , just get a reference to current dao

from features.configuration import Configuration

from models import dbconn, redisconn

from balance_notification_model import BalanceNotification
from balance_notification_dao import BalanceNotificationCachelDao, BalanceNotificationMysqlDao

BalanceNotification.sql_dao = BalanceNotificationMysqlDao( sql_conn = dbconn )
BalanceNotification.cache_dao = BalanceNotificationCachelDao( cache_conn = redisconn )



config_values  = Configuration.values()
mailer_host = config_values['mailer']['host']
mailer_port = config_values['mailer']['port']
