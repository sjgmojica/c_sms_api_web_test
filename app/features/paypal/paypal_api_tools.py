'''
this file executes paypal api calls

'''
#from geventhttpclient import HTTPClient
#from geventhttpclient.url import URL

import urllib

import urlparse 

from datetime import datetime

from . import api_merchant_user, api_merchant_paassword, api_merchant_signature, api_version, paypal_website_domain, website_callback_url,api_endpoint_url
from .paypal_token_model import PaypalToken

from . import mysql_dao
from tornado.httpclient import AsyncHTTPClient2, HTTPRequest

#--- ------
from pprint import pprint

class PaypalApiCaller( object ):
    
    transaction_success=None
    
    
    error_code=None
    short_message=None
    long_message = None
    
    
    general_error_msg  = ''
    
    def __init__(self):
        print 'init paypal caller'
        
    def __exit__(self,exc_type, exc_value, traceback):
        print 'destroy caller'

    def call_paypal( self, param_list=[] ):
        
        
        # reset transaction success
        self.transaction_success = None
        self.error_code=None
        self.short_message=None
        self.long_message = None
        
        uri = '/nvp'
        
        params = {
                  'USER' : api_merchant_user,
                  'PWD': api_merchant_paassword,
                  'SIGNATURE' : api_merchant_signature,
                  'VERSION': api_version ,
                  'L_PAYMENTREQUEST_n_ITEMCATEGORY0': 'Digital',
                  'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE'
                  }
        
        body = urllib.urlencode( params )
        
        if param_list:
            body = '%s&%s' % (body ,  '&'.join([ urllib.urlencode(y) for y in param_list   ])   )
        
        response_body = self.__call_via_https(method='post', uri=uri, params=body)
        
        
        #response_body = 'TOKEN=EC%2d20580220TS8020413&TIMESTAMP=2014%2d04%2d03T07%3a54%3a59Z&CORRELATIONID=52f1e29b6436&ACK=Success&VERSION=112&BUILD=10433064'
        
        parsed_data = urlparse.parse_qs(response_body)
        
        
        if type(parsed_data.get('ACK', None)) is list :
            if parsed_data['ACK'][0] == 'Success':
                self.transaction_success = True
            if parsed_data['ACK'][0] == 'Failure':
                
                
                self.error_code=parsed_data['L_ERRORCODE0'][0]
                self.short_message=parsed_data['L_SHORTMESSAGE0'][0]
                self.long_message = parsed_data['L_LONGMESSAGE0'][0]
                
                self.transaction_success = False
                
                self.general_error_msg = 'Failed to execute paypal call. %s ; %s ; %s ; params = %s' % ( self.error_code, self.short_message, self.long_message, repr(params) ) 
                
                
        else:
            raise PaypalGeneralError( 'paypal error, response is: %s'%response_body )
        
        return parsed_data

    def __call_via_https(self, method, uri, params):
        '''
        uri param is deprecated
        '''
        
        response_body = ''
        http = AsyncHTTPClient2()
        
        if method =='post':
            try:
                request = HTTPRequest(url=api_endpoint_url, method="POST", body=params)
                
                response = http.fetch(  request  )
                
                #response = http_conn.post( uri, body=params )
            
                response_body = response.body
            except Exception, e :
                raise PaypalTimeoutException('unable to process PAYPAL request: %s' % e)
            
        else:
            print 'unsupported method'
        
        #http_conn.close()
        
        return response_body

class PaypalExpressCheckout( PaypalApiCaller ):

    
    checkout_items = []
    total_transaction_amt = 0
    
    payer_id = None

    express_checkout_token = ''
    express_checkout_token_obj = None
    
    
    ready_for_payment = False
    
    #--- info for payment
    payment_action=None
    payment_currency_code=None
    
    payment_action_completed=None
    payment_action_in_progress=None
    checkout_status = None
    
    def __init__(self):
        
        self.checkout_items = []
        pass

    def add_checkout_item(self, desc, cost, qty):
        
        current_count = len( self.checkout_items )
        # BECAUSE SOME PARAMETERS NEED TO HAVE A SPECIFIC ORDERING 
        self.checkout_items.append( {'L_PAYMENTREQUEST_0_DESC%s'%current_count : desc, 'L_PAYMENTREQUEST_0_AMT%s'%current_count: cost, 'L_PAYMENTREQUEST_0_QTY%s'%current_count: qty } )
        
        self.total_transaction_amt += cost*qty

    def set_token_obj(self, token_obj  ):
        self.express_checkout_token_obj = token_obj 
    
    def get_paypal_checkout_url( self ):
        
        
        uri='/cgi-bin/webscr'
        domain = paypal_website_domain
        
        params = {'cmd':'_express-checkout', 'token': self.express_checkout_token_obj.token_string, 'useraction': 'commit'  }
        
        url = 'https://%s%s?%s' % (domain, uri, urllib.urlencode(params)  )
        
        return url

    def get_express_checkout_details(self, allow_only_verified=True):

        if not self.express_checkout_token_obj:
            return

        param_list = [
                      {'METHOD':'GetExpressCheckoutDetails'},
                      {'TOKEN': self.express_checkout_token_obj.token_string }
                      ]
        
        response_data = self.call_paypal( param_list  )
        
        
        if self.transaction_success is True :
            
            #self.payment_action=None
            self.payment_currency_code=response_data['PAYMENTREQUEST_0_CURRENCYCODE'][0]
            self.total_transaction_amt = response_data['PAYMENTREQUEST_0_AMT'][0]  
            
            
            self.checkout_status = response_data['CHECKOUTSTATUS'][0]
            
            if self.checkout_status != 'PaymentActionNotInitiated' :
                
                if self.checkout_status == 'PaymentActionCompleted' :
                    self.payment_action_completed = True
                    # checkout has already been paid, set to PAID
                    self.express_checkout_token_obj.set_paid()
            
                elif self.checkout_status == 'PaymentActionInProgress' :
                    self.payment_action_in_progress = True
            else:
                
                if allow_only_verified and response_data['PAYERSTATUS'][0] =='unverified':
                    raise UnverifiedUserException('paypal user with email %s is reported to be UNVERIFIED' % response_data['EMAIL'][0])
                
                
                if response_data.get('PAYERID', None) is not None:
                    self.payer_id = response_data['PAYERID'][0]
                    self.ready_for_payment = True
                    
                else:
                    self.express_checkout_token_obj.set_failed()
        else:
            self.express_checkout_token_obj.set_failed()

    def do_express_checkout_payment(self ):
        
        if self.payer_id and self.express_checkout_token_obj:
            param_list = [
                      {'METHOD':'DoExpressCheckoutPayment'},
                      {'TOKEN': self.express_checkout_token_obj.token_string },
                      {'PAYERID': self.payer_id },
                      {'PAYMENTREQUEST_0_PAYMENTACTION' : 'Sale'},
                      {'PAYMENTREQUEST_0_CURRENCYCODE' : self.payment_currency_code },
                      {'PAYMENTREQUEST_0_AMT' : self.total_transaction_amt },
                      ]
        

            response_data = self.call_paypal( param_list  )

            if response_data and response_data.get('ACK', None) is not None :
                if response_data['ACK'][0] =='Success':
                    self.express_checkout_token_obj.set_paid( paypal_transaction_id=response_data['PAYMENTINFO_0_TRANSACTIONID'][0]  )
                else:
                    print 'ack is not success',response_data['ACK']
                
        else:
            print 'missing token'
        
    
    def set_express_checkout( self, transaction_desc='', callback_uri='', custom_params={} ):
        '''
        execute paypal api call to create the express checkout
        '''
        
        #--- experiment
        import hashlib
        
        m = hashlib.md5()
        m.update('hello'+datetime.now().strftime('%S'))
        digest = m.hexdigest()

        #--- experiment
        
        
        if not callback_uri:
            callback_uri = '/paypal/confirm/'
        
        return_url = website_callback_url+callback_uri
        
        
        param_list = [   
                      { 'METHOD': 'SetExpressCheckout' },
                      {'PAYMENTREQUEST_0_CURRENCYCODE' : 'PHP'},
                      {'PAYMENTREQUEST_0_AMT' : self.total_transaction_amt},
                      {'PAYMENTREQUEST_0_ITEMAMT' : self.total_transaction_amt },
                      {'cancelUrl': website_callback_url },
                      {'returnUrl': return_url}
                      ]
        
        if transaction_desc :
            param_list.append( {'PAYMENTREQUEST_n_DESC' : transaction_desc}  )
        
        param_list+=self.checkout_items
        
        response_data = self.call_paypal( param_list  )
        
        # expects reponse to be something like this
        #{'ACK': ['Success'], 'TIMESTAMP': ['2014-04-03T07:54:59Z'], 'TOKEN': ['EC-20580220TS8020413'], 'VERSION': ['112'], 'BUILD': ['10433064'], 'CORRELATIONID': ['52f1e29b6436']}
        
        if self.transaction_success is True :
            # save token in mysql database
            token_obj = PaypalToken( token_string=response_data['TOKEN'][0], 
                                     date_created=datetime.strptime( response_data['TIMESTAMP'][0]  , "%Y-%m-%dT%H:%M:%SZ"),
                                     checkout_id=custom_params['checkout_id'] )
            token_obj.save()
            
            self.express_checkout_token_obj = token_obj
        else:
            raise PaypalGeneralError('could not contact paypal for express checkout: %s' % self.general_error_msg )
        
    def get_one_paypal_token_for_payment(self):
        
        
        pass
        
#         paypal_token_record = mysql_dao.get_one_for_payment()
#         
#         if paypal_token_record:
#             self.express_checkout_token = paypal_token_record['token']
#         
#         print paypal_token_record 
        

class PaypalGeneralError( Exception ):
    pass

class UnverifiedUserException( Exception ):
    pass

class PaypalTimeoutException( Exception ):
    pass