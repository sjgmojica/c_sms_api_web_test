'''
    @author:  Jhesed Tacadena
    @description:
        - provides locking mechanism for payment modules
            especiall dragonpay
'''
import gevent 
import time

EXPIRATION = 180  # seconds

class LockCacheDao(object):
    '''
        @description:
            - provides locking mechanism for cache key
    '''
    
    def __init__(self, conn=None, logger=None):
        '''
            @description:
                - class constructor: initializes
                cache connection and logger
        '''
        self.conn = conn
        self.log = logger
    
    def lock(self, key):
        '''
            @description: 
                - locks a cache key so that
                other apps will not be able to
                use this key
                - returns True if key
                is locked else False
        '''
        
        try:
            current_time = float(time.time())
            clock = int(self.conn.setnx(key, str(current_time)))
            lock_flag = True if clock == 0 else False
                 
            if lock_flag:  
                # key already exists, key is already locked
                self.log.info('[locking] key is locked, stopping process', {'key': key})
                return True
            
            self.log.info('[locking] key is NOT locked, acquired lock', {'key': key})
            self.conn.expire(key, EXPIRATION) # expires the key
            return False
            
        except Exception, e:
            self.log.error('[locking] lock exception', {'error': str(e)})
            return False
            
    def unlock(self, key):
        '''
            @description:
                - unlocks a key
        '''
        try:
            self.conn.delete(key)
        except Exception, e:
            self.log.error('[locking] unlock exception', {'error': str(e)})
        
        