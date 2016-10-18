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
    from features.paypal.paypal_checkout_model import PaypalPaymentCheckout
    
    from features.paypal import paypal_main    
    
    from datetime import datetime
    
    test_account = Account.get( account_id = 4 )
    
    PaypalPaymentCheckout.get_total_purchases_current_month( account_id=test_account.account_id )
    
    #PaypalPaymentCheckout.paypal_cache_dao.clear_monthly_paypal_purchase( account_id=test_account.account_id, date_reference=datetime.now()  )
    
    
     

    
