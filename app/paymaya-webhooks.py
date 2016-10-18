'''
    @author: Sarz and makmakulet
    @description:
        - paymaya call this api to validate the pending checkout_id
    @date: 2016-10-14
'''
from tornado.web import RequestHandler
from features.logging as sms_api_logger
from features.paymaya import paymaya_main

class CheckoutHookSuccessHandler (RequestHandler):
    def post(self):
        logger = sms_api_logger.GeneralLogger()
        checkout_id = self.argument('checkout_id')
        logger.info('start :: CheckoutHookSuccessHandler :: checkout_id =', checkout_id)
        print checkout_id

        #update details on paymaya_checkout to success
        params = {
            'receipt_number' : response_body['receiptNumber'] or  "",
            'transaction_reference_number' : response_body['transactionReferenceNumber'] or "",
            'status' : response_body['status'],
            'payment_status' :  response_body['paymentStatus']
        }

        paymaya_main.update_paymaya_checkout_details(checkout_id, params)
        paymaya_main.on_payment_webhook_success(checkout_id)
        logger.info('end :: CheckoutHookSuccessHandler')
        self.finish()

class CheckoutHookFailedHandler (RequestHandler):
    def post(self):
        logger = sms_api_logger.GeneralLogger()
        checkout_id = self.argument('checkout_id')
        logger.info('start :: CheckoutHookFailedHandler :: checkout_id =', checkout_id)
        print checkout_id

        #update details on paymaya_checkout to failure
        params = {
            'receipt_number' : response_body['receiptNumber'] or  "",
            'transaction_reference_number' : response_body['transactionReferenceNumber'] or "",
            'status' : response_body['status'],
            'payment_status' :  response_body['paymentStatus']
        }

        paymaya_main.update_paymaya_checkout_details( checkout_id, params)
        paymaya_main.on_payment_webhook_failed( checkout_id )
        logger.info('end :: CheckoutHookFailedHandler')
        self.finish()

application = tornado.web.Application([
    (r"/paymaya/webhooks/success", CheckoutHookSuccessHandler),
    (r"/paymaya/webhooks/failed", CheckoutHookFailedHandler)
])

if __name__ == "__main__":
    http_server = tornado.http_server.HTTPServer(application)
    tornado.ioloop.IOLoop.instance().start()
