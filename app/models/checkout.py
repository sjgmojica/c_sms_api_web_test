from utils.text_api import send_pincode, send_generic_sms

from datetime import datetime


class Checkout( object ):
    
    #--- configured statically
    db_dao = None
    purchase_history_dao = None
    #--- -----------
    
    
    
    checkout_id = None
    account_id = None
    suffix = None
    phone = None
    code = None
    amount = None
    
    # python datetime object
    date_expiry = None
    mode_of_payment = None 
    status  = None
    retry_ctr = None
    
    # python datetime object
    date_created = None
    
    # python datetime object
    date_updated = None
    expired = None
    remarks = None
    
    # used to identify the transaction saved in add credits
    credit_trans_id = None
    

    error_messages = []
    
    
    
    #--- constants
    #--- statuses
    STATUS_PENDING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILURE = 3
    
    
    
    def  __init__(self):
        
        pass
    
    @staticmethod
    def get( checkout_id ):
        
        
        checkout_object = Checkout.db_dao.get( checkout_id=checkout_id )
        
        return checkout_object
    
    @staticmethod
    def get_for_payment( checkout_id ):
        
        checkout_object = Checkout.db_dao.get_for_payment( checkout_id=checkout_id )
        
        return checkout_object
    
    def mark_successfully_paid(self):
        '''
        marks the checkout as successfully paid
        '''
        
        result = Checkout.db_dao.mark_paid_success( checkout_id=self.checkout_id )
        
        return result
    
    
    def mark_payment_failed(self):
        
        result = Checkout.db_dao.mark_payment_failed( checkout_id=self.checkout_id )
        
        return result
    
    
    
    @staticmethod
    def get_carrier_charging( ):
        '''
        retrieves a mapping of the current charging cost per carrier
        '''
        
        return Checkout.db_dao.get_carrier_charging()
        
    @staticmethod
    def get_all_purchase_history(account_id, limit=None, page=1   ):
        '''
            retrieves all the purchase history
            with @param account_id
        '''
        return Checkout.purchase_history_dao.get_all_purchase_history(
            account_id,
            limit=limit, 
            page=page)
     

    @staticmethod
    def get_purchase_history_page_count( account_id, items_per_page ):
        
        total_pages=1
        
        try :
            total_pages = Checkout.purchase_history_dao.get_total_pages( account_id=account_id, items_per_page=items_per_page )
        except Exception, e:
            raise PurchaseHistoryReadError('unable to get items from purchase history / checkout')
        
        return total_pages

     
    def write_to_purchase_history(self):
        print 'MODEL: WRITE TO HISTORY'
        try:
            Checkout.purchase_history_dao.new_purchase_history( self )
        except Exception, e:
            logger.error( 'unable to get paymaya express checkout. try again: %s' % e, {'account_id': account_id }  )        

    def write_pending_purchase_history(self):
        
        Checkout.purchase_history_dao.set_pending_purchase_history_record( self )

    
    @staticmethod
    def get_items( checkout_id ):
        '''
        retrieves checkout items from database
        
        '''
        
        data_result = Checkout.db_dao.get_checkout_items(checkout_id=checkout_id)
        
        return data_result
        
        
    def get_checkout_items(self):
        '''
        @author: vincent agudelo 2014-04-04
        retrieves checkout items from the checkout
        it should be a list (of dicts) that looks like this
        [{'qty': 2, 'cost': 100.0, 'name': u'PLAN 100', 'desc': u'Up to 250 messages.'}]  
        '''
        
        items = Checkout.db_dao.get_checkout_items(  checkout_id=self.checkout_id  )
        
        return items 
        
    

    
class SmartPaymentGatewayCheckout( Checkout ):
    '''
    this is a type of checkout that is specific to smart payment gateway mode
    there are functions here for smart payment gateway only 
    
    '''

    sms_resend_ctr=0

    @staticmethod
    def get( checkout_id ):
        checkout_object = Checkout.db_dao.get_smart_payment_checkout( checkout_id=checkout_id )
        
        return checkout_object
    
    def send_payment_PIN_code(self):
        '''
        this is executed each time the payment process starts (after user input his amsrt mobile number)
        
        this will just
        - send the sms 
        '''
        
        message_id = None

        # send pincode to user with his/her suffix
        sms_body = """CHIKKA API: Your PIN code for transaction %s is %s.
        
Please enter this code to complete your purchase."""% (self.checkout_id, self.code)
        
        message_id = send_generic_sms( phone=self.phone ,body=sms_body )

        
        return message_id
    
    def resend_payment_PIN_code(self):
        '''
        this is an optional activity where the user may want to send the pin code again
        
        
        upon exedcution the following will take effect
        1. send the sms
        2. increment the resend counter
        3. update the expiry date (to current time
        '''
        sms_body = """CHIKKA API: Your PIN code for transaction %s is %s.
        
Please enter this code to complete your purchase."""% (self.checkout_id, self.code)
        
        message_id = None

        # increment ctr and extend expiry
        # do not wait for the sms to be sent before incrementing this !!!
        # that is why this comes first
        try:
            extend_seconds = (30*60) # @todo get from config
            Checkout.db_dao.increment_sms_resend( checkout_id=self.checkout_id, extend_seconds=extend_seconds )
        except Exception, e:
            print 'unable to update db', e
            self.error_messages.append( 'unable to updated database: %s' % e )

        
        try:
            message_id = send_generic_sms( phone=self.phone ,body=sms_body )
        except Exception, e:
            self.error_messages.append( 'unable to resend sms: %s' % e )
            
        
        
        
        
    
        return message_id    
    
    
    
    
class CheckoutReadError( Exception ):
    pass

class CheckoutSaveError( Exception ):
    pass

class CarrierChargeReadError( Exception ):
    pass

class PurchaseHistoryReadError( Exception ):
    pass

class PurchaseHistoryWriteError( Exception ):
    pass

class CheckoutExpiredError( Exception ):
    pass

class CheckoutNotExistError( Exception ):
    pass