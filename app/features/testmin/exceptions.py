'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

# --- ENROLLMENT ---

class EmptyMinException(Exception): 
  
    def __init__(self):     
        pass
    
    def __str__(self):
        return ('EMPTY TESTMIN')
        
class InvalidTestminException(Exception): 
    testmin = None

    def __init__(self, testmin):     
        self.testmin = testmin
    
    def __str__(self):
        return ('TESTMIN %s IS INVALID' %self.testmin)

class MaxUnverifiedMinEnrollmentsException(Exception): 
    account_id = None

    def __init__(self, account_id):     
        self.account_id = account_id
    
    def __str__(self):
        return ('ACCOUNT %s ENROLLED UNVERIFIED TESTMINS MORE THAN ALLOWED' %self.account_id)
      
class TestminPreviouslyVerifiedException(Exception):
    account_id = None
    testmin = None
    
    def __init__(self, account_id, testmin):     
        self.account_id = account_id
        self.testmin = testmin
    
    def __str__(self):
        return ('TESTMIN %s -- %s PREVIOUSLY VERIFIED' %(self.account_id, self.testmin))
          
class MaxChangeMinException(Exception): 
    account_id = None
    
    def __init__(self, account_id):     
        self.account_id = account_id
    
    def __str__(self):
        return ('ACCOUNT %s CHANGED TESTMIN MORE THAN ALLOWED' %self.account_id)
       
class MaxCodeRequestsException(Exception):
    account_id = None
    testmin = None
    
    def __init__(self, account_id, testmin):     
        self.account_id = account_id
        self.testmin = testmin
    
    def __str__(self):
        return ('ACCOUNT %s -- %s REQUESTED CODE RESENDS MORE THAN ALLOWED' %(self.account_id, self.testmin))
              
# --- Code Verification ---

class MaxWrongCodeTriesException(Exception):
    account_id = None
    testmin = None
    code = None
    
    def __init__(self, account_id, testmin, code):     
        self.account_id = account_id
        self.testmin = testmin
        self.code = str(code)
    
    def __str__(self):
        return ('MAX WRONG CODE TRIES: %s -- %s -- %s' %(self.code, self.account_id, self.testmin))

class WrongCodeException(Exception):
    account_id = None
    testmin = None
    code = None
    
    def __init__(self, account_id, testmin, code):     
        self.account_id = account_id
        self.testmin = testmin
        self.code = str(code)
    
    def __str__(self):
        return ('CODE %s -- %s -- %s INVALID' %(self.code, self.account_id, self.testmin))
        
class ExpiredCodeMaxCodeRequestException(Exception):
    account_id = None
    testmin = None
    code = None
    
    def __init__(self, account_id, testmin, code):     
        self.account_id = account_id
        self.testmin = testmin
        self.code = str(code)
    
    def __str__(self):
        return ('CODE %s -- %s -- %s EXPIRED MAX REQUESTS' %(self.code, self.account_id, self.testmin))
        
class ExpiredCodeException(Exception):
    account_id = None
    testmin = None
    code = None
    
    def __init__(self, account_id, testmin, code):     
        self.account_id = account_id
        self.testmin = testmin
        self.code = str(code)
    
    def __str__(self):
        return ('CODE %s -- %s -- %s EXPIRED' %(self.code, self.account_id, self.testmin))
        