from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

from datetime import datetime



def test_set_balance():
    
    account_object = Account.get( account_id=4 )
    
    #enable_balance_notification( account_object=account_object, threshold=150 )
    #enable_balance_notification( account_object=None, threshold=100 )
    
    disable_balance_notification( account_object )
    



if __name__ == '__main__':


    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()
    
    from features.account_management.balance_notif_main import disable_balance_notification, enable_balance_notification, send_balance_threshold_notif, send_zero_credit_notif, inspect_balance_for_notif
    from models.account import Account
    
    test_set_balance()
    
    # test send email to me
    #send_balance_threshold_notif( email='vagudelo@chikka.com', threshold=100, date_notif=datetime.now() )
    
    #send_zero_credit_notif( email='vagudelo@chikka.com', shortcode=924507, expiry_date=datetime.now() )
    
    
    #data = '54b521448cc96df2027d90cf547de09da949f0dbd2c75e493d1803a83df8081f:925407'
    #data = '54b521448cc96df2027d90cf547de09da949f0dbd2c75e493d1803a83df8081f:9909'
    
    #client_id, suffix = data.split(':')
    
    
    
    #inspect_balance_for_notif( client_id=client_id, suffix=suffix )