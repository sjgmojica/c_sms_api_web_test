'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from re import compile

# Used for converting characters
# to its corresponding number equivalents

CHAR_NUM_CONVERSION = {
    '2': ['a', 'b', 'c'],
    '3': ['d', 'e', 'f'],
    '4': ['g', 'h', 'i'],
    '5': ['j', 'k', 'l'],
    '6': ['m', 'n', 'o'],
    '7': ['p', 'q', 'r', 's'],
    '8': ['t', 'u', 'v'],
    '9': ['w', 'x', 'y', 'z']
}

def is_mobile_format_valid(mobile):
    '''
        @description:
            - returns True if mobile
            is valid, else False
    '''
    valid_mobile = compile('(63|0|\+63)?[9][0-9]{2,2}[0-9]{7,7}$')
    if not valid_mobile.match(mobile):
        return False
    return True
    
def alpha_to_numeric(starts_with=''):
    '''
        @description:
            - converts @param starts_with
            (if it is string) to its equivalent
            numeric representation
    '''
    numeric_str = ''
    for c in starts_with:
        if c.isalpha():
            for n in CHAR_NUM_CONVERSION:
                if c.lower() in CHAR_NUM_CONVERSION[n]:
                    numeric_str += n
                    break
        else:
            numeric_str += c
    return numeric_str
    
    

class InvalidMobileFormatException(Exception): 
    mobile = None

    def __init__(self, mobile):     
        self.mobile = mobile
    
    def __str__(self):
        return ('MOBILE %s IS INVALID' %self.mobile)
        
class MobileNotSmartException(Exception): 
    account_id = None
    mobile = None

    def __init__(self, account_id, mobile):     
        self.account_id = account_id
        self.mobile = mobile
    
    def __str__(self):
        return ('%s -- MOBILE %s IS NOT SMART' %(
            self.account_id, self.mobile))
            
            
class MobileNotGlobeException(Exception): 
    '''
        @description:
            - used only to cater temporary
            unworking MO and MT using SUN and
            SMART
    '''
    account_id = None
    mobile = None

    def __init__(self, account_id, mobile):     
        self.account_id = account_id
        self.mobile = mobile
    
    def __str__(self):
        return ('%s -- MOBILE %s IS NOT GLOBE' %(
            self.account_id, self.mobile))
            