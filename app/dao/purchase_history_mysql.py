'''
writes to purchase history

generally it's just a copy of the checkout object but in another table

'''


#from models.checkout import Checkout

TABLE_PURCHASE_HISTORY = 'purchase_history'

class PurchaseHistoryMysqlDAO( object ):
    
    payment_type_value = 'SMART'
    
    sql_util = None
    table_name='purchase_history'
    
    def __init__(self, sql_util):
        self.sql_util = sql_util
    
    def get(self):
        pass
    
    def get_total_pages(self, account_id, items_per_page):
        '''
        retrieves total page count of purchase histoy
        '''
        
        page_count = 5
        
        criteria = {'account_id':account_id}
        try:
            table_cols = ['COUNT(checkout_id)']
            result = self.sql_util.execute_select( table_name=self.table_name, 
                conditions=criteria, 
                table_cols=table_cols, 
                fetchall=False )
            
            page_count = result['COUNT(checkout_id)']/items_per_page
            if result['COUNT(checkout_id)']%items_per_page:
                page_count+=1
            
        except Exception, e :
            raise PurchaseHistoryReadError('error while retrieving purchase history data: %s' % e)
        
        return page_count

    def get_all_purchase_history(self, account_id, limit=None, page=1 ):
        '''
            @description:
                - returns a list of all purchase history from
                DB with @param account_id
        '''
        criteria = {'account_id' : account_id}
        table_cols = [
            'checkout_id',    
            'date_purchased',
            'amount',
            'mode_of_payment',
            'status',
            'webtool_reference_id'
        ]
       
       
        pageparams = {}
        if limit:
            pageparams = {'limit':limit, 'offset': (page-1)*limit }
            
        print pageparams 
        try:
            return self.sql_util.execute_select(
                table_name=TABLE_PURCHASE_HISTORY, 
                conditions=criteria, 
                operator='AND', table_cols=table_cols, 
                fetchall=True, orderby=['date_purchased'], order='DESC', **pageparams)
                  
        except Exception, e:
            print e
        return None
    
    
    def new_purchase_history(self , checkout_object ):
        '''
        creates a new transaction history from the checkout object 
        
        '''
        
        fields = {}
        fields['account_id'] = checkout_object.account_id
        fields['suffix'] = checkout_object.suffix
        #fields['plan_code']
        fields['amount'] = checkout_object.amount
        fields['date_purchased'] = checkout_object.date_updated.strftime('%Y-%m-%d %H:%M:%S')
        #fields['days_valid']
        fields['mode_of_payment'] = checkout_object.mode_of_payment
        fields['remarks'] = checkout_object.remarks
        
        if checkout_object.status == checkout_object.STATUS_FAILURE:
            fields['status'] = 'FAILURE'
        if checkout_object.status == checkout_object.STATUS_SUCCESS:
            fields['status'] = 'SUCCESS'
        if checkout_object.status == checkout_object.STATUS_PENDING:
            fields['status'] = 'PENDING'
        
        fields['checkout_id'] = checkout_object.checkout_id
        fields['credit_trans_id'] = checkout_object.credit_trans_id
        
        
        
        self.sql_util.execute_insert_update( table_name='purchase_history', insert_params=fields, 
                              update_params=fields)
        
        #self.__insert_to_db( fields=fields )

    def set_pending_purchase_history_record(self, checkout_object ):
        
        fields = {}
        fields['account_id'] = checkout_object.account_id
        fields['suffix'] = checkout_object.suffix
        fields['amount'] = checkout_object.amount
        fields['date_purchased'] = checkout_object.date_updated.strftime('%Y-%m-%d %H:%M:%S')
        fields['mode_of_payment'] = checkout_object.mode_of_payment
        fields['remarks'] = checkout_object.remarks
        fields['status'] = 'PENDING'
        fields['checkout_id'] = checkout_object.checkout_id
        fields['credit_trans_id'] = checkout_object.credit_trans_id
        
        #self.sql_util.execute_insert_update( table_name='purchase_history', insert_params=fields, 
        #                      update_params=fields)
        self.__insert_to_db( fields=fields )


    def _get_total_purchase_per_type_per_month(self, account_id, payment_type, date_reference  ):
        
        print 'get total purchase per type'
        
        try:
            result = self.sql_util.run_query( 'select', 
                                          """select SUM(amount) as total 
                                          from purchase_history 
                                          where account_id=%s && mode_of_payment='%s' && status='SUCCESS' && date_purchased like "%s%%";""" % ( account_id, payment_type, date_reference.strftime('%Y-%m')),
                                          dictionary=True,
                                          fetchall=False )
            if result:
                if result['total'] :
                    return result['total']
                else:
                    return 0
            else:
                return 0
            
        except Exception, e :
            raise PurchaseHistoryReadError('unable to fetch total purchases for %s : %s' % (   payment_type,  e  ))
        
        
        
        
    def __insert_to_db(self, fields ):
        
        try :
            result = self.sql_util.execute_insert('purchase_history', fields)
            if int(result) <= 0: 
                 raise PurchaseHistoryWriteError('unable to write to purchase history: data %s ; %s' % ( repr(fields), e ) )
        except Exception, e :
            raise PurchaseHistoryWriteError('unable to write to purchase history: data %s ; %s' % ( repr(fields), e ) )
        
class PurchaseHistoryReadError( Exception ):
    pass