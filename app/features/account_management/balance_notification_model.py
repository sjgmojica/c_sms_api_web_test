


class BalanceNotification( object ):
    
    
    cache_dao = None
    sql_dao = None
    
    def __init__(self):
        
        pass
    
    
    @staticmethod
    def pop_balance_notif( ):
        
        
        # get notif from cache
        
        popped_value = BalanceNotification.cache_dao.pop_notification()
        
        return popped_value
    
    @staticmethod
    def pop_balance_backup_notif( ):
        
        popped_value = BalanceNotification.cache_dao.pop_backup_notification()
        
        return popped_value
    
    @staticmethod
    def pop_out_backup_queue():

        BalanceNotification.cache_dao.pop_out_backup_queue()
        
        