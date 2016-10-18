


class BalanceNotificationMysqlDao( object ):
    
    sql_conn = None
    
    def __init__(self, sql_conn = None):
        
        self.sql_conn = sql_conn
        


class BalanceNotificationCachelDao( object ):
    
    cache_conn = None
    
    balance_notification_queue_key = 'chikka_api_balance_notif_queue'
    
    balance_notification_queue_bkup_key = 'chikka_api_balance_notif_bkup_queue'
    
    
    def __init__(self, cache_conn = None):
        
        self.cache_conn = cache_conn
        

    def pop_backup_notification(self):

        popped_value = self.cache_conn.rpoplpush( self.balance_notification_queue_bkup_key, self.balance_notification_queue_key )
        
        return popped_value


        
    def pop_notification(self):
        
        popped_value = self.cache_conn.brpoplpush( self.balance_notification_queue_key, self.balance_notification_queue_bkup_key )
        
        
        return popped_value
        
    def pop_out_backup_queue(self):
        '''
        pops out end of a queue to limbo
        
        '''
        self.cache_conn.rpop( self.balance_notification_queue_bkup_key )
        