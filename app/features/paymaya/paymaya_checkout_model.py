'''
this encapsulates the saved paypal token
@author: sarz - makmakulet ;)

'''

class PaymayaCheckout( object ):
    
    checkout_id = None
    paymaya_checkout_id = None
    status = None
    payment_status = None
    
    db_util = None
    cache_dao = None
    
    pending_check_ctr = 0
    
    
    def __init__(self, token_string, date_created, checkout_id ):
        
        self.token_string = token_string
        self.date_created = date_created
        self.checkout_id = checkout_id
        
    def save(self):
        '''
        saves the new paypal token
        '''
        print 'MODEL: saving token'
        PaypalToken.db_util.save_token( token_string=self.token_string, 
                              token_date_str=self.date_created.strftime( '%Y-%m-%dT%H:%M:%SZ' ), 
                              custom_params={ 'checkout_id':self.checkout_id } 
                              )
    @staticmethod
    def get( token_str=None, checkout_id=None ):
        '''
        retrieves a paypal token object via paypal token str
        
        as of 2014-07-10 a paypal token string looks like this:
        EC-1PS74505GX948234P
        20 characters
        
        token can also be retrieved via checkout id since  it is more safe.
        also one paypal payment is for only one payment
        
        either token string OR checkout id is used BUT NOT both
        '''
        if token_str and checkout_id is None :
            # @todo add filtering HERE
            
            # 20 characters that look like this:
            # EC-1AB21265G7829454A
            # A-Z0-9\-
            
            if len(token_str) is 20:
                matchto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
                for x in token_str:
                     if x not in matchto:
                         return None
                     
                t_obj = PaypalToken.db_util.get_paypal_token( token_str=token_str )
                return t_obj
                     
            else:
                return None

            
        elif token_str is None and checkout_id  :
            t_obj = PaypalToken.db_util.get_paypal_token_by_checkout_id( checkout_id=checkout_id )
            return t_obj
        else:
            return None
    

    @staticmethod
    def get_one_pending():
        '''
        retrieves one pending paypal token data
        
        first checks redis x number of times before checking via sql
        
        if redis has a flag saying that there is a new pending data, sql is checked right away
        '''
        token_obj = None

        max_redis_check = 5
        
        if max_redis_check == PaypalToken.pending_check_ctr:
            token_obj = PaypalToken.get_one_paypal_pending_token_from_db()
            PaypalToken.pending_check_ctr = 0
        else:
            PaypalToken.pending_check_ctr += 1
            pending_exists = PaypalToken.check_pending_payment()
            if pending_exists :
                token_obj = PaypalToken.get_one_paypal_pending_token_from_db()

        return token_obj

    @staticmethod
    def get_one_paypal_pending_token_from_db( ):
        token_obj = None
        
        paypal_token_record = PaypalToken.db_util.get_one_for_payment()
        
        if paypal_token_record:
        
            # return a new pending paypal token
            token_obj = PaypalToken( token_string=paypal_token_record['token'],
                     date_created = paypal_token_record['token_date_created'],
                     checkout_id = paypal_token_record['checkout_id']
                     )        
            
            if paypal_token_record['remaining'] is True:
                # set the pending cache flag
                # will be processed during next iteration of checking
                print 'there is remaining payment, setting flag'
                PaypalToken.cache_dao.set_pending_payment()
        
        
        
        return token_obj

    @staticmethod
    def check_pending_payment( ):
        

        return PaypalToken.cache_dao.check_pending_payment()        
        

    
    def set_pending(self):
        # set status pending
        result = PaypalToken.set_token_pending( token=self.token_string )
        
        if result :
            # set flag in cache to indicate pending payment
            PaypalToken.cache_dao.set_pending_payment()
        else:
            print 'because result is', result

    @staticmethod
    def set_token_pending( token ):
        result = PaypalToken.db_util.set_pending( token=token )
        return result

    
    def set_charging(self):
        success = PaypalToken.db_util.set_charging( token=self.token_string )
        
        return success
        

    def set_paid(self, paypal_transaction_id ):
        PaypalToken.db_util.set_paid( token=self.token_string, paypal_transaction_id=paypal_transaction_id )


    def set_failed(self):
        PaypalToken.db_util.set_fail( token=self.token_string )

    def set_unverified_user_payment(self):
        '''
        if user paid via paypal and is not verified by paypal
        a flag must be set
        
        this flag is to infor the notification screen. no harm will be done
        if this fails. payment will still not proceed 
        
        '''
        try:
            checkout_id = int(self.checkout_id)
            result = PaypalToken.cache_dao.set_unverified_payment_by_user(checkout_id=checkout_id)
            
        except Exception, e:
            raise Exception('could not write to cache server: %s' % e)


    @staticmethod
    def test_failed_by_unverified_paypal_account( checkout_id ):
        '''
        retrieves from cache info if paypal payment failed
        because of it was paid via UNVERIFIED paypal account
        
        !!! WARNING !!!
        
        value in cache disappears (expires) calling this method
        long after payment was executed will ALWAYS evaluate to FALSE  
        
        '''
        
        try:
            checkout_id = int(checkout_id)
            result = PaypalToken.cache_dao.test_error_via_unverified_paypal( checkout_id=checkout_id )
            
        except:
            result = False
        
        return result