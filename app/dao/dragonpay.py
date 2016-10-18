'''
    @author:  Jhesed Tacadena
    @date: 2014-10
'''

from models.dragonpay import Dragonpay

TABLE_DRAGONPAY = 'dragonpay'

class DragonpayDao(object):
    '''
        @description:
            - contains set of functions for
            obtaining DB/cache data for
            dragonpay transactions
    '''
    
    def __init__(self, dbconn):
        self.dbconn = dbconn
        
    def get(self, txn_id):
        '''
            @description
                - returns the dragonpay data
                from DB with passed txn_id
            @param txn_id:
                - transaction id
                - format: CHKID_<txn_id>
        '''
        
        criteria = {'txn_id': txn_id}
        table_cols = [
            'txn_id',
            'refno',
            'ctoken_id',
            'status',
            'message'
        ]
        
        try:
            result = self.dbconn.execute_select(
                table_name=TABLE_DRAGONPAY, conditions=criteria,
                table_cols=table_cols, fetchall=False
            )
            return result
            
        except Exception:
            import traceback
            print traceback.format_exc()
            
        return None    
     
   
    def is_ctoken_valid(self, txn_id, ctoken_id):
        '''
            @description
                - returns True if there exists a 
                txn_id and ctoken_id referencing
                to the same row, else False
            @param txn_id:
                - transaction id
                - format: CHKID_<txn_id>
            @param ctoken_id:
                - unique ID 
        '''
        
        criteria = {
            'txn_id': txn_id,
            'ctoken_id': ctoken_id            
        }
        table_cols = [
            'txn_id'
        ]
        
        try:
            result = self.dbconn.execute_select(
                table_name=TABLE_DRAGONPAY, conditions=criteria,
                table_cols=table_cols, fetchall=False, operator='AND')
            return True if result else False
            
        except Exception:
            import traceback
            print traceback.format_exc()
            
        return False
    
    
    def save(self, **kwargs):
        '''
            @description:
                - saves dragonpay data in
                TABLE_DRAGONPAY
        '''
        
        if 'txn_id' not in kwargs:
            return False
        
        params = {
            'txn_id': kwargs['txn_id']
        }
        
        if 'refno' in kwargs:
            params['refno'] = kwargs['refno']
        if 'ctoken_id' in kwargs:
            params['ctoken_id'] = kwargs['ctoken_id']
        if 'status' in kwargs:
            params['status'] = kwargs['status']
        if 'message' in kwargs:
            params['message'] = kwargs['message']
            
        try:
            
            result = self.dbconn.execute_insert(
                table_name=TABLE_DRAGONPAY, params=params)
               
        except Exception:
            import traceback
            print traceback.format_exc()
        
        return result
        
        
    def update(self, **kwargs):
        '''
            @description:
                - updates dragonpay data in
                TABLE_DRAGONPAY
        '''
        
        if 'txn_id' not in kwargs:
            return False
        
        criteria = {
            'txn_id': kwargs['txn_id']
        }
        
        params = {}
        
        if 'refno' in kwargs:
            params['refno'] = kwargs['refno']
        if 'ctoken_id' in kwargs:
            params['ctoken_id'] = kwargs['ctoken_id']
        if 'status' in kwargs:
            params['status'] = kwargs['status']
        if 'message' in kwargs:
            params['message'] = kwargs['message']
            
        try:
            
            if params:
                result = self.dbconn.execute_update(
                    table_name=TABLE_DRAGONPAY,
                    params=params, conditions=criteria
                )
                
        except Exception:
            import traceback
            print traceback.format_exc()
        
        return False
        