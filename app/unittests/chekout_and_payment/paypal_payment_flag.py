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
    
    from features.paypal.paypal_checkout_model import PaypalPaymentCheckout

    checkout = PaypalPaymentCheckout.get( checkout_id=372 ) 
    #checkout.set_paypal_pending_payment_flag()

    checkout.clear_paypal_pending_payment_flag()



    print 'flag is for', checkout.get_paypal_pending_payment_flag( account_id=checkout.account_id )