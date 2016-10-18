'''
this is the DAO class for paypal cache

'''

class PaypalRedisDao( object ):
    
    
    # about 1.5 month expiration
    monthly_paypal_purhcase_cache_expiration = 3888000 # seconds
    redisconn = None
    
    pending_payment_key = "chikka_api_paypal_pending_payment_signal"
    
    
    #account id : month_year : paypal_purchase_total
    accumulated_purchase_key = '%s:%s:paypal_purchase_total'
    
    paypal_pending_payment_flag_ttl = 60
    
    
    def __init__(self, redisconn=None, config_mode='debug', paypal_pending_payment_flag_ttl=60 ):
        self.pending_payment_key = '%s:%s' %  ( config_mode,  "chikka_api_paypal_pending_payment_signal" )
        
        self.redisconn = redisconn
        
        self.paypal_pending_payment_flag_ttl = paypal_pending_payment_flag_ttl

    def set_pending_paypal_payment_flag(self, account_id, checkout_id ):
        
        key = 'chikkaapi:pending_paypal:%s' % str(account_id)
        value = checkout_id
        
        key_ttl = self.paypal_pending_payment_flag_ttl
        try:
            result = self.redisconn.setex( key, str(value), key_ttl )
        except Exception, e:
            raise PaypalCacheException('unable to write pending paypal payment flag for account_id=%s; checkout_id=%s; %s' % ( account_id, checkout_id, e ) )
        


    def get_pending_paypal_payment_flag(self, account_id):
        
        key = 'chikkaapi:pending_paypal:%s' % str(account_id)
        
        try:
            result = self.redisconn.get( key )
        except Exception, e:
            raise PaypalCacheException('unable to read pending paypal payment flag for account_id=%s; %s' % ( account_id, e ) )
        
        return result
        
    def clear_pending_paypal_payment_flag(self, account_id):
        
        key = 'chikkaapi:pending_paypal:%s' % str(account_id)
        print key
        try:
            result = self.redisconn.delete( key )
            print 'delete result', result
        except Exception, e:
            raise PaypalCacheException('unable to clear pending paypal payment flag for account_id=%s; %s' % ( account_id, e ) )


        
    
    def check_pending_payment(self):
        try:
            pending_payment_exists = self.redisconn.getset( self.pending_payment_key, "False")
            
            if pending_payment_exists =='True':
                print 'returning', True
                return True
            else:
                print 'returning', False
                return False
            

        except Exception, e:
            raise PaypalCacheException( 'exception rasied while checking for pending payment in cache: %s.'% e )
            

    def set_pending_payment(self):
        
        try:
            pending_payment_exists = self.redisconn.set( self.pending_payment_key, "True")
        except Exception, e:
            raise PaypalCacheException('unable to set pending payment flag: %s' % e)

    
    def set_unverified_payment_by_user(self, checkout_id):
        
        
        key = 'cid:%s:unverifiedpaypalused' % checkout_id
        value = "True"
        try:
            result = self.redisconn.setex( key, value, 120 )
        except Exception, e:
            raise PaypalCacheException('unable to write: %s | key=%s value=%s' % (e, key, value) )
        
            
    def test_error_via_unverified_paypal(self, checkout_id):
        '''
        retrieves flag from cache. uses checkout id 
        
        '''
        
        key = 'cid:%s:unverifiedpaypalused' % checkout_id
        result = self.redisconn.get( key )
        if result :
            return True
        else:
            return False
        
    def get_total_purchases_for_month(self, account_id, date_reference  ):
        

        # %s:%s_%s:paypal_purchase_total'
        
        month_format = date_reference.strftime('%m_%Y')
        
        key = self.accumulated_purchase_key % ( account_id,  month_format ) 

        result = None

        try:
            result = self.redisconn.get( key )
        except Exception, e:
            raise PaypalCacheException('unable to get value for key %s' % key)        
        
        print 'cache result', result
        
        return result
    
    def set_total_purchases_for_month(self, account_id, date_reference, value  ):
        # for cache rebuilding ONLY
        

        # %s:%s_%s:paypal_purchase_total'
        
        month_format = date_reference.strftime('%m_%Y')
        
        key = self.accumulated_purchase_key % ( account_id,  month_format ) 

        result = None

        try:
            
            expiration =  self.monthly_paypal_purhcase_cache_expiration
             
            
            result = self.redisconn.setex( key,  str(value), expiration )
        except Exception, e:
            raise PaypalCacheException('unable to set value for key %s = %s; %s' %  (key, value, e)  )        
        
        return result
    
    def clear_monthly_paypal_purchase(self, account_id, date_reference  ):
        '''
        to be used in emergency situations
        
        '''
        month_format = date_reference.strftime('%m_%Y')
        key = self.accumulated_purchase_key % ( account_id,  month_format )

        try:
            
            result = self.redisconn.delete( key )
        except Exception, e:
            raise PaypalCacheException('unable to delete  key %s ; %s' %  (key, e)  )        

        
        

    def increment_monthly_paypal_purchase(self, account_id, date_reference, amount):
        '''
        increments the monthly
        '''
        
        month_format = date_reference.strftime('%m_%Y')
        key = self.accumulated_purchase_key % ( account_id,  month_format )
        
        try:
            
            print 'amount=%s' % amount
            result = self.redisconn.incrby( key, amount )
            

        
        except Exception, e:
            print e
            raise PaypalCacheException( 'unable to increment paypal purchase amount: %s' % e )

        try:
            # if the value is the same as the given amount,
            # it means that the key may not exist before this instance
            # set expiration
            if result == amount:
                result = self.redisconn.expire( key, self.monthly_paypal_purhcase_cache_expiration )        
        
        except Exception, e:
            raise PaypalCacheException( 'unable to set expiration to monthly paypal purchase cache: %s' % e )
        
 
        




class PaypalCacheException( Exception ):
    pass