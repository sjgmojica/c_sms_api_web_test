'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

class CartEmptyException(Exception): 
    account_id = None

    def __init__(self, account_id):     
        self.account_id = account_id
    
    def __str__(self):
        return ('%s CART IS EMPTY' %self.account_id)


class IncorrectPincodeException(Exception): 
    account_id = None
    pincode = None

    def __init__(self, account_id, pincode):     
        self.account_id = account_id
        self.pincode = pincode
    
    def __str__(self):
        return ('%s -- %s PINCODE INVALID' %(self.account_id, self.pincode))
        
class ExpiredPincodeException(Exception): 
    account_id = None
    pincode = None

    def __init__(self, account_id, pincode):     
        self.account_id = account_id
        self.pincode = pincode
    
    def __str__(self):
        return ('%s -- %s PINCODE EXPIRED' %(self.account_id, self.pincode))

class MaxCodeRetriesException(Exception): 
    account_id = None
    pincode = None

    def __init__(self, account_id, pincode):     
        self.account_id = account_id
        self.pincode = pincode
    
    def __str__(self):
        return ('%s -- %s PINCODE EXPIRED' %(self.account_id, self.pincode))
        
        
class CheckoutQueuePushException(Exception): 
    account_id = None
    checkout_id = None

    def __init__(self, account_id, checkout_id):     
        self.account_id = account_id
        self.checkout_id = checkout_id
    
    def __str__(self):
        return ('%s -- %s ERROR PUSHING TO CHECKOUT QUEUE' %(self.account_id, self.checkout_id))
    
class PaymentMethodError(Exception):
    pass