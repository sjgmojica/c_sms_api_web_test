'''
@author: vincent agudelo


this script runs a a listener 

that will listen to a redis list and execute the balance notification feature



'''
import gevent
from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

parse_command_line()
from features.configuration import Configuration

Configuration.initialize()
    
#values = Configuration.values()


import features.logging as chikka_sms_api_logger
from features.account_management.balance_notification_model import BalanceNotification

from features.account_management.balance_notif_main import inspect_balance_for_notif

l = chikka_sms_api_logger.GeneralLogger()

def notif_process():
    
    
    l.info('starting balance notification app')
    # recover items from queue
    # loop each item in bckup queue
    while True:
        # flushes out backup queue until empty
        popped_value = BalanceNotification.pop_balance_backup_notif()
        if not popped_value:
            break
        
        # process this value
        parse_data( data=popped_value )

    # start regular loop
    while True :
        
        popped_value = BalanceNotification.pop_balance_notif()
        l.info('read data from queue', popped_value)
        parse_data( data=popped_value )
        # remove popped value from backup queue
        BalanceNotification.pop_out_backup_queue()


def parse_data( data ):
    
    try :
        client_id, suffix = data.split(':')
        inspect_balance_for_notif( client_id=client_id, suffix=suffix )
        
    except Exception , e:
        l.error('error in parsing data: %s'%e, data )

def main():
    notif_process()


if __name__ == '__main__':
    gevent.spawn(main).join()