'''
@author: this is the interface object that must be implemented in the paymaya mysql DAO

'''
from datetime import datetime, timedelta
class PaymayaDAOInterface ():
    '''
    must implement these functions
    '''
    
    sql_util=None
    
    def save_token(self, token_string, token_date_str=None, custom_params={} ):
        
        # adjust for GMT+8
        gmt_8_delta = timedelta(hours=8)
        t_date_created = datetime.strptime( token_date_str, '%Y-%m-%dT%H:%M:%SZ' ) + gmt_8_delta
        
        self.create( token=token_string, token_date_created=t_date_created, custom_params=custom_params )


    def create(self, token, token_date_created, custom_params={} ):
        pass


    def set_pending(self, token):
        return False
        
    
    def set_paid(self, token, paypal_transaction_id):
        '''
        method to set the status of paypal token to paid
        this is usually when expresspayment is successful
        '''
        
        return False
        
    def set_charging(self, token):
        '''
        CHARGING is set when the checkout is confirmed as ready for payment
        '''
        return False
    
    def set_fail(self, token):
        '''
        in case express checkout payment fails for some reason  (i.e. token expiry / max request)
        this will be set to fail
        '''
        
        return False
    
    def get_one_for_payment(self):
        '''
        retrieves one record from paypal tokens
        '''
        print '*** if you are seeing this message, it means you forgot to implement this function in your DAO ***'
        
        return None
    
    
class DummyDao(  object, PaymayaDAOInterface):
    
    pass