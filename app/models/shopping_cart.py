'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

class ShoppingCart( object ):
    
    dao = None
    
    def __init__(self):
        self.id = None
        self.account_id = None
        self.suffix = None
        self.phone = None
        self.code = None
        self.amount = None
        self.date_expiry = None
        self.mode_of_payment = None
        self.status = None
        self.retry_ctr = 0
        self.expired = '0'
    
    # --- checkout ---
    
    @staticmethod
    def get_checkout(account_id, checkout_id=None, 
        phone=None, expired='0'):
         return ShoppingCart.dao.get_checkout(
            account_id, checkout_id, phone, expired)
    
    @staticmethod
    def save_checkout(account_id, checkout_dict):
        return ShoppingCart.dao.save_checkout(
            account_id, checkout_dict)
        
    @staticmethod
    def update_checkout_expired(checkout_id):
        return ShoppingCart.dao.update_checkout_expired(
            checkout_id)
        
    @staticmethod
    def update_checkout_status_to_pending(checkout_id):
        return ShoppingCart.dao.update_checkout_status_to_pending(
            checkout_id)
        
    """
    @staticmethod
    def incr_retry_ctr(checkout_id):
        return ShoppingCart.dao.incr_retry_ctr(
            checkout_id)
    """
     
    # --- checkout items ---
    
    @staticmethod
    def save_checkout_items(cart_dict):
        return ShoppingCart.dao.save_checkout_items(cart_dict)
    
    @staticmethod
    def get_checkout_items(checkout_id):
        return ShoppingCart.dao.get_checkout_items(checkout_id)