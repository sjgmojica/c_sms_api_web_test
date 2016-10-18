'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from models.shopping_cart import ShoppingCart
from datetime import datetime, timedelta
import features.logging as sms_api_logger

TABLE_CHECKOUT = 'checkout'
TABLE_CHECKOUT_ITEMS = 'checkout_items'

class ShoppingCartDao(object):
    
    def __init__(self, dbconn):
        self.dbconn = dbconn
                         
    # ----------------
    # --- CHECKOUT ---
    # ----------------
                         
    def get_checkout(self, account_id, checkout_id=None, phone=None, expired='0'):
        criteria = { 
            'account_id' : account_id,
            'expired' : expired
        }
        if checkout_id:
            criteria['id'] = checkout_id
        if phone:
            criteria['phone'] = '639%s' %phone[-9]
         
        table_cols = [
            'id',
            'account_id',
            'suffix',
            'phone',
            'code',
            'amount',
            'date_expiry',
            'mode_of_payment',
            'status',
            'retry_ctr',
            'expired'
        ]
        
        try:
            result = self.dbconn.execute_select(
                table_name=TABLE_CHECKOUT, 
                conditions=criteria, 
                operator='AND', table_cols=table_cols, 
                fetchall=False)
             
            if result:
                cart_obj = ShoppingCart()
                cart_obj.id = result['id']
                cart_obj.account_id = result['account_id']
                cart_obj.suffix = result['suffix']
                cart_obj.phone = result['phone']
                cart_obj.code = result['code']
                cart_obj.amount = result['amount']
                cart_obj.date_expiry = result['date_expiry']
                cart_obj.mode_of_payment = result['mode_of_payment']
                cart_obj.status = result['status']
                cart_obj.retry_ctr = result['retry_ctr']
                cart_obj.expired = result['expired']
            
                return cart_obj
   
        except Exception, e:
            print e
        return False
        
        
    def save_checkout(self, account_id, checkout_dict):
    
        phone = ('639%s' %checkout_dict['phone'][-9:]) if checkout_dict['phone'] else ''
        params = {
            'account_id': account_id,
            'phone': phone,
            'code': checkout_dict['code'],
            'amount': checkout_dict['amount'],
            'date_expiry': checkout_dict['date_expiry'],
            'mode_of_payment' : checkout_dict['mode_of_payment'],
            # 'retry_ctr' : 1,
            'date_created' : datetime.now(),
            'suffix' : checkout_dict['suffix'],
            'expired' : '0'
        }

        if 'status' in checkout_dict:
            params['status'] = checkout_dict['status']  # for dragonpay
            
        
        scart_logger = sms_api_logger.SCartLogger()
     
        try:
  
            result = self.dbconn.execute_insert(
                table_name=TABLE_CHECKOUT, params=params)
               
            scart_logger.info('SUCCESS -- saving CHECKOUT to DB', 
                {'account_id' : account_id})        
            
            return result
            
        except Exception, e:
            scart_logger.error('ERROR -- saving CHECKOUT to DB', 
                {'account_id' : account_id, 'error': str(e)})   
            print e
            
    def update_checkout_expired(self, checkout_id):
        criteria = {
            'id' : checkout_id
        }
        params = {
            'expired': '1',
            'date_updated': datetime.now()
        }
        
        scart_logger = sms_api_logger.SCartLogger()
        
        try:
        
            result = self.dbconn.execute_update(table_name=TABLE_CHECKOUT,
                params=params, conditions=criteria)
        
            scart_logger.info('SUCCESS -- updating CHECKOUT EXPIRATION', 
                {'checkout_id' : checkout_id})           
            
            return result
        
        except Exception, e:
            scart_logger.error('ERROR -- updating CHECKOUT EXPIRATION', 
                {'checkout_id' : checkout_id, 'error': str(e)})           
            print e
   
    def update_checkout_status_to_pending(self, checkout_id):
              
        query_str = "UPDATE checkout SET status='PENDING', date_updated='%s' WHERE status is NULL AND expired=0 AND id=%s" %(
            datetime.now(), checkout_id)
        
        scart_logger = sms_api_logger.SCartLogger()
        
        try:   
        
            self.dbconn.run_query('update', query_str)
            
            scart_logger.info('SUCCESS -- checkout status to PENDING', 
                {'checkout_id' : checkout_id})        
                
        except Exception, e:            
            scart_logger.error('ERROR -- checkout status to PENDING', 
                {'checkout_id' : checkout_id, 'error': str(e)})  
            print e
        
    """
    def incr_retry_ctr(self, checkout_id):
        query_str = 'UPDATE %s SET retry_ctr=retry_ctr+1 WHERE id=%s' %(
            TABLE_CHECKOUT, checkout_id)
        
        try:
            return self.dbconn.run_query('update', query_str, dictionary=True)
        except Exception, e:
            print e
    """ 
                
    # ----------------------
    # --- CHECKOUT ITEMS ---
    # ----------------------
     
    def save_checkout_items(self, cart_dict):
        '''
            @param cart_item: (dict)
        '''
        if not cart_dict:
            return None

        scart_logger = sms_api_logger.SCartLogger()
         
        params = {
            'plan_code': cart_dict['plan_code'],
            'checkout_id': cart_dict['checkout_id'],
            'amount': cart_dict['amount'],
            # 'days_valid': cart_dict['days_valid'],
            'date_created': datetime.now(),
            'quantity': cart_dict['quantity']
        }
        
        try:
            result = self.dbconn.execute_insert(
                table_name=TABLE_CHECKOUT_ITEMS, params=params)
            
            scart_logger.info('SUCCESS -- saving checkout ITEMS to DB', 
                {'checkout_id' : cart_dict['checkout_id']})                       
            
            return result   
   
        except Exception, e:
            scart_logger.error('ERROR -- saving checkout ITEMS to db', 
                {'checkout_id' : cart_dict['checkout_id'], 'error': str(e)})              
            print e
    
    def get_checkout_items(self, checkout_id):
        criteria = {
            'checkout_id': checkout_id
        }
        table_cols = [
            'checkout_id',
            'plan_code',
            'quantity',
            'amount'
        ]
        
        try:
            return self.dbconn.execute_select(
                table_name=TABLE_CHECKOUT_ITEMS, 
                conditions=criteria, 
                operator='AND', table_cols=table_cols, 
                fetchall=True)
                
        except Exception, e:
            print e
        return False