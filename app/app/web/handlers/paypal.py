from tornado.web import authenticated, asynchronous
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

import features.paypal.paypal_api_tools as paypal_api_tools

from features.paypal.paypal_main import check_payment_if_success
 
from features.payments.payment import receive_paypal_callback, PaypalPaymentError

import features.logging as sms_api_logger_tool


 
import ujson as json 

@route('/paypalnotif/([0-9a-z]+)/([0-9]+)')
class PaymentNotification( BaseHandlerSession ):
    
    @authenticated
    @asynchronous    
    def get(self, hash, checkout_id):
        
        token_str = self.get_argument('token', None)
        data = {'result': None, 'verified': False}
        data['result'], data['verified'] = check_payment_if_success( token=token_str, checkout_id=checkout_id, hash=hash)
        
        self.write( json.dumps(data) )
        self.finish()


@route('/testpaypal')
class PaypalTestHandler( BaseHandlerSession ):
    
    
    def get(self):
        
        
        paypal_caller = paypal_api_tools.PaypalExpressCheckout()
        
        paypal_caller.add_checkout_item(desc='item1', cost=17.00, qty=2)
        paypal_caller.add_checkout_item(desc='item2', cost=3.00, qty=3)
        
        
        try:
            paypal_caller.set_express_checkout()
            
            
            if paypal_caller.transaction_success is True:
                
                self.redirect( paypal_caller.get_paypal_checkout_url()  )
            else:
            
                self.write('paypal')
                self.finish()
                
        except Exception, e:
            
            self.write('exception rasied while accessing paypal: %s' % e)
            self.finish()
            
@route('/paypal/confirm/([0-9a-z]+)/([0-9]+)')
class PaypalCheckoutConfirm( BaseHandlerSession ):
    
    @authenticated
    @asynchronous
    def get(self, hash, checkout_id ):
        
        logger = sms_api_logger_tool.PaymentLogger()
        logger.info('receiving paypal payment')
        
        message = 'paypal confirmed'
        
        token_str = self.get_argument('token', None)
        
        logger.info('using token', token_str)
        
        formatted_amount = ''
        
        try:
            checkout_object = receive_paypal_callback( token=token_str, account_id=self.current_user.account_id, checkout_id=checkout_id, hash=hash )


            formatted_amount = 'P%.2f' % checkout_object.amount

        except Exception, e:
            logger.error('error occured during paypal payment', str(e) )
            self.redirect('/cart')

        else:
            message = 'paypal confirmed'
            #self.write('paypal confirmed')
            
        
            self.render('page-paypal-payment-confirmed.html', 
                        message=message, 
                        token_str=token_str, 
                        checkout_id=checkout_id, 
                        hash=hash,
                        amount=formatted_amount
                        )