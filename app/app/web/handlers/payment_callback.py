'''
special handler that will accept the callback calls from smart payment gateway


FOR INTERNAL USE ONLY

@author: vincent agudelo
'''
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

from tornado.web import asynchronous, authenticated
from models.dragonpay import Dragonpay

from features.payments.dragonpay.dragonpay import *

from urlparse import parse_qs, urlparse
import features.payments.checkout as checkout_payment 
from features.payments.spiels import SPIELS
import features.logging as sms_api_logger

import utils.smart_payment_tool as smart_payment_tool
from models.lock_cache import LockCache


@route('/smart_payment_callback')
class SignupVerificationHandler( BaseHandlerSession ):
    
    
    def post(self):
        payment_logger = sms_api_logger.PaymentLogger()
        
        payment_logger.info('received payment callback')
        uri_params_string = self.request.uri.replace('/smart_payment_callback', '')
        
        params_dict = {}
        
        qs =  urlparse( self.request.uri )
        
        payment_logger.info( 'using uri',self.request.uri)
        
        callback_response_body = self.request.body
        payment_logger.info('callback body', callback_response_body)
        
        
        if qs :
            try :
                qparams = parse_qs( qs.query )
                
                payment_logger.info('using params', qparams)
                
                for key,value in qparams.iteritems() :
                    
                    if key == 'aid' :
                        params_dict['account_id'] = value[0]
                        
                    elif key == 'cid' : 
                        params_dict['checkout_id'] = value[0]
                    
            
                # process checkout as PAID
                checkout_payment.on_payment_success(  callback_response = callback_response_body,    checkout_id=params_dict['checkout_id'], account_id=params_dict['account_id'] )
                
                payment_logger.info( 'payment sequence finalized' )
            
            except Exception, e :
                payment_logger.error('exception raised while receiving payment callback', e)
            
                
                
        self.write('ok')
        
        
@route('/dragonpay/status/update')
class DragonPayCallbackHandler(BaseHandlerSession):
    '''
        @author:  Jhesed Tacadena
        @description:
            - handles dragonpay callback.
            - updates DB/cache if dragonpay 
              transaction was successful
            - example:
                dragonpay/status/update?txnid=CHKID_78&refno=FXYG8U63&status=D&message=1234&digest=de64127f38fb34be4a7e41ff7462a16b047c8409&param1=1394184009.64_EJT9
    '''
    def post(self):
    
        payment_logger = sms_api_logger.PaymentLogger()
        
        txn_id = self.get_argument('txnid')
        refno = self.get_argument('refno')
        status = self.get_argument('status')
        message = self.get_argument('message')
        lock_key = 'lock:%s' % str(txn_id)
        
        
        # --- locking ---
        
        
        if LockCache.lock(key=lock_key):
            # locks txn to avoid multiple processes
            return
        
        else:
            # ! you should delete this once URL was already encoded !
            # message = message.replace('000', '[000]')
            
            digest = self.get_argument('digest')
            ctoken_id = self.get_argument('param1', None)
            
            is_digest_valid = validate_dragonpay_digest(txn_id=txn_id, refno=refno,
                status=status, message=message, dragonpay_digest=digest, ctoken_id=ctoken_id)
            
            if not is_digest_valid:
            
                # --- invalid dragonpay digest ---
            
                payment_logger.error('DRAGONPAY INVALID DIGEST', {'txn_id': txn_id,
                    'refno': refno, 'status': status, 'message': message,
                    'digest': digest, 'ctoken_id': ctoken_id})
                    
                LockCache.unlock(key=lock_key)
                
                return
            
            is_ctoken_valid = Dragonpay.is_ctoken_valid(txn_id=txn_id, ctoken_id=ctoken_id)
                    
            if not is_ctoken_valid:
            
                # --- invalid ctoken digest ---
            
                payment_logger.error('DRAGONPAY INVALID CTOKEN', {'txn_id': txn_id,
                    'refno': refno, 'status': status, 'message': message,
                    'digest': digest, 'ctoken_id': ctoken_id})
                    
                LockCache.unlock(key=lock_key)
                
                return
            
            # -- updates status in dragonpay table in DB ---
            
            try:
                Dragonpay.update(txn_id=txn_id, refno=refno, status=status,
                    message=message)        

                payment_logger.info('DRAGONPAY SUCCESS UPDATING DB', {'txn_id': txn_id,
                    'refno': refno, 'status': status, 'message': message,
                    'digest': digest, 'ctoken_id': ctoken_id})
                
            except Exception, e:
                payment_logger.error('DRAGONPAY UNABLE TO UPDATE DB', {'txn_id': txn_id,
                    'refno': refno, 'status': status, 'message': message,
                    'digest': digest, 'ctoken_id': ctoken_id})
                return
            
            
            # -- process callback --
            
            if status in ['R', 'K']:  # Refund | Chargeback
                
                # ! to be implemented. waiting for business rules !
                
                payment_logger.info('DRAGONPAY STATUS IN [REFUND | CHANGEBACK]', 
                    {'txn_id': txn_id, 'refno': refno, 'status': status, 
                    'message': message, 'digest': digest, 'ctoken_id': ctoken_id})

                            
            elif status in ['P', 'U']:  # pending


            
                # unknown's behavior is unpredictable
                
                payment_logger.info('DRAGONPAY STATUS IN [PENDING | UNKNOWN]', 
                    {'txn_id': txn_id, 'refno': refno, 'status': status, 
                    'message': message, 'digest': digest, 'ctoken_id': ctoken_id})
                
            else:
                good_response = True if status == 'S' else False
               
                # --- update DB and cache; the user paid successfully ---
                checkout_payment.on_payment_success_dragonpay(
                    txn_id=txn_id, good_response=good_response)

            

            
        LockCache.unlock(key=lock_key)
        return
        self.finish()
            
          
@route(['/dragonpay/status', '/dragonpay/status/'])
class DragonpayStatusHandler(BaseHandlerSession):
    '''
        @description:
            - handles the return URL callback
            from dragonpay (for display purpose)
    '''
    
    @asynchronous
    @authenticated
    def get(self):
        
        status = self.get_argument('status')
        
        message = ''
        if status == 'S':
            message = SPIELS['dsuccess']
        elif status == 'P':
            message = SPIELS['dpending']
        else:
            message = SPIELS['dfailed']
            
        self.render('plain.html',
            message=message)
        return
        
    