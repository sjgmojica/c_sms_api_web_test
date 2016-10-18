from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


if __name__ == '__main__':


    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()
    
    from models.account import Account
    from models.checkout import Checkout
    
    from features.paypal.paypal_main import increment_monthly_paypal_total_by
    
    from datetime import datetime
    
    test_account = Account.get( account_id = 4 )
     
    
     

    increment_monthly_paypal_total_by( account_id=test_account.account_id, date_reference=datetime.now(), amount=1.1 )
