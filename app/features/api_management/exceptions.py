'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

class InvalidPublicKeyException(Exception): 
    account_id = None
    suffix = None
    public_key = None

    def __init__(self, account_id, suffix, public_key):     
        self.account_id = account_id
        self.public_key = public_key
        self.suffix = suffix
    
    def __str__(self):
        return ('%s -- SUFFIX %s -- %s INVALID PUBLIC KEY' %(self.account_id, self.suffix, self.public_key))
        
        
class InvalidCallbackUrlException(Exception): 
    account_id = None
    suffix = None
    callback_url = None

    def __init__(self, account_id, suffix, callback_url):     
        self.account_id = account_id
        self.suffix = suffix
        self.callback_url = callback_url
        
    def __str__(self):
        return ('%s -- SUFFIX %s -- %s INVALID CALLBACK URL' %(self.account_id, self.suffix, self.callback_url))
        
        
class InvalidMoUrlException(Exception): 
    account_id = None
    suffix = None
    mo_url = None

    def __init__(self, account_id, suffix, mo_url):
        self.account_id = account_id
        self.suffix = suffix
        self.mo_url = mo_url
    
    def __str__(self):
        return ('%s -- SUFFIX %s -- %s INVALID MO URL' %(self.account_id, self.suffix, self.mo_url))