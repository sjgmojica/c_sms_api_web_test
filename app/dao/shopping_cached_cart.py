'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from ujson import dumps, loads
from models.shopping_cached_cart import ShoppingCachedCart

KEY = 'cart:%s'
#CHECKOUT_QUEUE_KEY = 'checkout_queue'
CHECKOUT_VALUE = 'cid:%s'


class ShoppingCachedCartDao(object):
    
    CHECKOUT_QUEUE_KEY = 'checkout_queue'
    
    
    def __init__(self, redisconn):
        self.redisconn = redisconn        
    
    def get_items(self, account_id):
        key = KEY % account_id 
        try:
            data = self.redisconn.get(key)
            if data:
                return loads(data)
            return None
        except Exception, e:
            # TO DO
            print e
    
    def save_item_to_cart(self, account_id, new_item):
        key = KEY % account_id
        try:
            self.redisconn.set(key, dumps(new_item))
        except Exception, e:
            # to do
            print e
        
    def wipe_out_cart(self, account_id):
        key = KEY % account_id
        try:
            self.redisconn.delete(key)
        except Exception, e:
            # to do
            print e   
            
    def push_to_checkout_queue(self, checkout_id):
        '''
            may be transferred to payment model and dao
            in future
        '''
        value = CHECKOUT_VALUE % str(checkout_id)
        try:
            return self.redisconn.lpush(
                self.CHECKOUT_QUEUE_KEY, value)
        except Exception, e:
            print e
            return 0
        
    def as_object(self, package):
        pass    