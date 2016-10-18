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
    from features.shopping_cart.shopping_cart import process_paypal_checkout, add_update_cart
    
    test_account = Account.get( account_id = 4 )
     
    
     
    new_item = {
            'id': 10, # 500 peso package
            'quantity': 2
        }
        
    chached_cart = add_update_cart(account_id=test_account.account_id, new_data=new_item)
    
    process_paypal_checkout( account_id=test_account.account_id, amount=   new_item['quantity'] *500     )