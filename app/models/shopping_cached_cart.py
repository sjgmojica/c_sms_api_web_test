'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

class ShoppingCachedCart(object):
    
    dao = None
      
    def __init__(self):
        pass
        
    @staticmethod
    def get_items(account_id):
        return ShoppingCachedCart.dao.get_items(
            account_id)
       
    @staticmethod    
    def save_item_to_cart(account_id, cached_cart):
        return ShoppingCachedCart.dao.save_item_to_cart(
            account_id, cached_cart)
        
    @staticmethod
    def wipe_out_cart(account_id):
        return ShoppingCachedCart.dao.wipe_out_cart(
            account_id)
    
    @staticmethod
    def push_to_checkout_queue(checkout_id):
        '''
            may be transferred to payment model and dao
            in future
        '''
        return ShoppingCachedCart.dao.push_to_checkout_queue(
            checkout_id)
        
    