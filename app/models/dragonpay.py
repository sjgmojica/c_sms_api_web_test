'''
    @author:  Jhesed Tacadena
    @date: 2014-03
'''

class Dragonpay(object):
    '''
        @description:
            - contains data definitions
            and function interface for
            saving dragonpay-transaction
            related data
    '''
    
    dao = None
    http_conn = None  # used for soap calls
    
    
    def __init__(self):
        
        # CHKID_<checkout_id>
        self.txn_id = None 
        
        # unique ID of transaction in dragonpay side
        self.refno = None  
        
        # in [S|F|P] (success/fail/pending) from dragonpay
        self.status = None 
        
        # <unix timestamp>_<random 4 characters>; 
        # used for validating authenticity of dragonpay
        self.ctoken_id = None 

        
    @staticmethod
    def get(txn_id):
        '''
            @param txn_id transaction ID
        '''
        return Dragonpay.dao.get(txn_id)
    
    @staticmethod
    def is_ctoken_valid(**kwargs):
        return Dragonpay.dao.is_ctoken_valid(**kwargs)
      
    @staticmethod
    def save(**kwargs):
        return Dragonpay.dao.save(**kwargs)
      
    @staticmethod
    def update(**kwargs):
        return Dragonpay.dao.update(**kwargs)
      