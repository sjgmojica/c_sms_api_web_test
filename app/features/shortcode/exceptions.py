
class ShortcodeFormatInvalidException(Exception): 
    account_id = None
    shortcode = None
    
    def __init__(self, account_id, shortcode):     
        self.account_id = account_id
    
    def __str__(self):
        return ('SHORTCODE %s -- %s FORMAT INVALID' %(self.shortcode, self.account_id))

class NoShortcodeMatchException(Exception):
    account_id = None
    shortcode = None
    
    def __init__(self, account_id, shortcode):     
        self.account_id = account_id
    
    def __str__(self):
        return ('NO SHORTCODE MATCH FOR %s -- %s' %(self.shortcode, self.account_id))
        
class NoSuffixException(Exception):
    account_id = None
    
    def __init__(self, account_id):
        self.account_id = account_id
        
    def __str__(self):
        return ('ACCOUNT %s NO SUFFIX' %str(self.account_id) )
        
        
class HasSuffixException(Exception):
    account_id = None
    
    def __init__(self, account_id):
        self.account_id = account_id
        
    def __str__(self):
        return ('ACCOUNT %s ALREADY HAS SUFFIX' %str(self.account_id) )