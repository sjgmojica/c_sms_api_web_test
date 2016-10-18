from dao.redis_dao import BaseDAORedis

from datetime import datetime


from utils.redis_tool import r_get, r_incr, r_expire, r_delete


class AccountCacheDAO( BaseDAORedis ):
    
    
    fail_login_attempt_ctr_format = 'login_fail:%s:%s'
    '''
    key format will be like this
    
    
    login_fail:1234:20131019'
    
    where 
      1234 is the account id
      
      20131019 is the date stamp (2013 10 19)
      
    so each key is unique per user per day virtually 'resetting' the counter each day
    
    expiration should also be implemented for cleanup
    
    '''

    suffix_cache_key_format = 'SMSAPI_%s'

    def get_free_credits(self, suffix ):
        
        free_credits = 0
        
        try :
            data = self.redis_conn.hgetall( 'SMSAPI_%s' % suffix )
            
            
            trial_credits = data[0:2]
            if trial_credits[0] == 'TRIAL_CREDITS':
                free_credits = trial_credits[1]
                
            
        except Exception, e:
            print 'unable to get credit data'
        
        return free_credits

    def update_secret_key(self, suffix, secret_key):
        
        
        try:
            self.redis_conn.hset( 'SMSAPI_%s' % suffix, 'SECRET_KEY', secret_key )
            
        except Exception, e:
            raise AccountCacheException( 'exception raised while trying to save secret key to cache, suffix=%s; secret_key=%s, error=%s' % (suffix, secret_key, e) )
        
        
        
    
    def increment_failed_attempted_login(self, account_id):
        '''
        just increments a key that is unique per user per day
        '''
        
        key = self.__build_failed_attempt_key( account_id=account_id )
        
        attempts = 0
        
        try :
            new_value = r_incr( conn=self.redis_conn, key=key )
            if new_value == 1 :
                r_expire( conn=self.redis_conn, key=key, expire_seconds=86400 )
            
            attempts = new_value
            
        except :
            pass

        return attempts
    
    def get_current_day_failed_attempts(self, account_id ):
        '''
        gets the failed attempts
        
        '''
        
        key = self.__build_failed_attempt_key( account_id=account_id )
        failed_attempts = 0

        try :
            
            failed_attempts = r_get( conn=self.redis_conn, key=key )
            
            if not failed_attempts :
                failed_attempts = 0

        except Exception, e :
            pass
        
        return failed_attempts

    def delete_failed_attempt_ctr(self, account_id ):
        key = self.__build_failed_attempt_key( account_id=account_id )

        try :
            
            r_delete( conn=self.redis_conn, key=key )

        except Exception, e :
            print 'exception rasied', e
            pass



    def __build_failed_attempt_key(self, account_id ):
        '''
        builds the key to use for failed login attempt counter
        '''
        
        key = self.fail_login_attempt_ctr_format % ( account_id, datetime.now().strftime('%Y%m%d') )
            
        return key 
    

    #--- functions for get/set of threshold notif sent and zero balance sent
    
    def set_zero_balance_notif_sent(self, suffix, sent=True ):
        '''
        set the flag that determines if zero balance notification
        for a particular suffix owner has been sent
        '''
        self.__set_balance_notif_sent_flag( suffix=suffix, field_key='ZERO_BALANCE_NOTIF_SENT', sent=sent)
         


    def get_zero_balance_notif_sent(self, suffix ):
        '''
        get the field value of flag that determines if
        the zero balance notif has been
        sent for a particular suffix owner
        '''

        sent = self.__get_balance_notif_sent_flag( suffix=suffix, field_key='ZERO_BALANCE_NOTIF_SENT' )
        return sent


    def set_balance_threshold_notif_sent(self, suffix, sent=True ):
        '''
        set flag that determines that the balance threshold has been reached
        '''
        
        self.__set_balance_notif_sent_flag( suffix=suffix, field_key='BALANCE_THRESHOLD_NOTIF_SENT', sent=sent)


    def get_balance_threshold_notif_sent(self, suffix ):
        '''
        get flag that determines that the balance threshold has been reached
        
        '''
        
        sent = self.__get_balance_notif_sent_flag( suffix=suffix, field_key='BALANCE_THRESHOLD_NOTIF_SENT' )
        return sent
 
    
    #--- core redis manipulation commands get set of suffix cache field data --------------------------------

    def __set_balance_notif_sent_flag(self, suffix, field_key, sent=True):
        '''
        generic setter for balance notif flags
        '''
        if sent :
            sent = str(sent)
            self.__set_cache_field_data( suffix=suffix, field_key=field_key , field_value=sent )
        else:
            self.__del_cache_field_data( suffix=suffix, field_key=field_key  )        



    def __get_balance_notif_sent_flag(self, suffix, field_key ):
        '''
        generic getter for balance notif sent flag
        '''
        
        sent = False
        result = self.__get_cache_field_data( suffix=suffix, field_key=field_key )
        if result :
            # cheaper to just see if result has value than comparing if "True" or "False"
            sent= True


        return sent

    
    def __set_cache_field_data(self, suffix, field_key , field_value ):
        '''
        set the field data of the user account suffix
        
        '''
        
        try:
            key = self.suffix_cache_key_format % suffix
            self.redis_conn.hset( key, field_key, field_value )
            #print 'set %s %s %s' % (key, field_key, field_value) 
            
        except Exception, e:
            raise AccountCacheException('ACCOUNT CACHE. unable to set field %s to value %s : %s' % (field_key,  field_value,  e) )
        
    def __get_cache_field_data(self, suffix, field_key ):
        '''
        retrieve a field data from a user suffix account
        a user account is bound to a suffix as long as the client id in database is
        the same in the field data of this cache
        
        '''

        result = None

        try:
            result = self.redis_conn.hget( self.suffix_cache_key_format % suffix, field_key )
            
        except Exception, e:
            raise AccountCacheException('ACCOUNT CACHE. unable to get field value %s : %s' % (field_key, e)  )        
                
        return result
        

    def __del_cache_field_data(self, suffix, field_key ):
        '''
        used rarely when a field date is to be erased
        '''
        result = None

        try:
            key = self.suffix_cache_key_format % suffix
            
            self.redis_conn.hdel( key, field_key )
            #print 'delete', key
            
        except Exception, e:
            raise AccountCacheException('ACCOUNT CACHE. unable to get field value %s : %s' % (field_key, e)  )        

    
    
class AccountCacheException( Exception ):
    pass