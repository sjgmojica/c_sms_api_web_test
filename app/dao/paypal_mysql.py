'''
@author: vincent agudelo
this DAO will be in charge of transacting with the application's databse
for storring/updating PayPal tokens

requires some sort of sql util 
'''





# use paypal dao interface
from features.paypal.dao_interface import PaypalMySqlDAOInterface

from features.paypal.paypal_token_model import PaypalToken

class PaypalMysqlDAO( object, PaypalMySqlDAOInterface ):
    
    
    paypal_token_table_name='paypal_tokens'
    
    def __init__(self, sql_util):
        
        
        self.sql_util = sql_util
        
        pass
    
    
    def create(self, token, token_date_created, custom_params={} ):
        '''
        paypal payments are tied to a signgle chika api checkout
        
        
        @param checkout_id: the id of the checkout record
        @param token : the 20-character string token from PayPal
        @param token_date_created: datetime object that defines the time the token was created
        
        '''
        
        checkout_id = custom_params.get('checkout_id', None)
        
        try:
            params = {'checkout_id' : checkout_id, 'token': token, 'token_date_created' : token_date_created.strftime('%Y-%m-%d %H:%M:%S')  }
            print 'using params for DB', params
            result = self.sql_util.execute_insert( table_name=self.paypal_token_table_name, params=params)
            
        except Exception, e:
            raise PaypalDaoException('could not write token record: %s' % e)
        
        return result
    
    def set_paid(self, token, paypal_transaction_id):
        '''
        method to set the status of paypal token to paid
        this is usually when expresspayment is successful
        
        paypal transaction id must be saved
        
        '''


        params = {'status' : 'PAID', 'trans_id': paypal_transaction_id}
        conditions = {'token' : token}
        return self._update_fields(params=params, conditions=conditions)




    def set_pending(self, token):
        '''
        PENDING is set when the checkout is confirmed as ready for payment
        '''
        return self._set_status(token=token, status='PENDING', ext_params={ 'status': None })


        
    def set_charging(self, token):
        '''
        CHARGING is set when checkout is in payment procedure
        '''
        return self._set_status(token=token, status='CHARGING', ext_params ={ 'status': 'PENDING' } )
    
    def set_fail(self, token):
        '''
        in case express checkout payment fails for some reason  (i.e. token expiry / max request)
        this will be set to fail
        '''
        
        return self._set_status(token=token, status='FAIL')
    
    def get_paypal_token(self, token_str):
        '''
        retrieves paypal token via token str
        '''
        conditions = {'token' : token_str }
        return self.__get_paypal_token(conditions )


    def get_paypal_token_by_checkout_id(self, checkout_id):
        '''
        retrieves paypal token via checkout id
        '''
        conditions = {'checkout_id' : checkout_id }
        return self.__get_paypal_token( conditions )

    def __get_paypal_token(self, conditions ):
        token_object = None
        fields = ['id', 'checkout_id', 'token', 'status', 'token_date_created']
        token_record = self.__retrieve( fields=fields, conditions=conditions, limit=1  )
        if token_record :
            token_object = PaypalToken( token_string = token_record['token'], 
                                        date_created = token_record['token_date_created'] , 
                                        checkout_id = token_record['checkout_id'] )
        
        return token_object

    def get_one_for_payment(self):
        '''
        implementation
        fetches one record from database that should be for payment
        status=NULL
        
        
        will get at most two (2) records but will return only one record and indicate that there may be another record
        '''
        record = None
        try:
            
            query = 'SELECT `id`, `checkout_id`, `token`, `status`, `token_date_created` FROM `paypal_tokens` WHERE `status`="PENDING" LIMIT 2;'
            
            records = self.sql_util.run_query( query_type='select', query=query , fetchall=True)
        
            if records:
                record = records.pop()
                # if still contains
                if records:
                    record['remaining'] = True
                else:
                    record['remaining'] = False
            
            
        except Exception, e:
            raise PaypalDaoException('could not read paypal token record: %s' % e)
        
        return record         
        
    def __retrieve(self, fields, conditions, limit=None  ):
        
        record = None
        
        try:

            checkout_table = 'paypal_tokens'
            
            record = self.sql_util.execute_select(
                table_name=checkout_table, 
                conditions=conditions, 
                operator='AND', table_cols=fields, 
                limit=limit, fetchall=False)
            
        except Exception, e:
            raise PaypalDaoException('could not read paypal token record: %s' % e)
        
        return record        
        
    
    def _set_status(self, token, status, ext_params={} ):
        
        params = {'status' : status}
        conditions = {'token' : token}
        
        conditions.update(ext_params)

        return self._update_fields(params=params, conditions=conditions)

        
    def _update_fields(self, params, conditions  ):
        
        
        try:

            result = self.sql_util.execute_update( table_name=self.paypal_token_table_name, params=params, conditions=conditions, operator="&&")
            if result:
                return True
            else:
                return False

        except Exception, e:
            raise PaypalDaoException('could not update record: %s' % e)
    
class PaypalDaoException( Exception ):
    pass