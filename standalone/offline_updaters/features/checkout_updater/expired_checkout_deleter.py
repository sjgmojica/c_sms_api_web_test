'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
        - removes expired checkouts after 1 week of expiration
'''


from utils.configuration import Configuration
from utils.sql_tools import SQLUtils
import features.logging as sms_api_logger

class ExpiredCheckoutDeleter(object):

    dbconn = None
    
    def main(self):
        '''
            @description:
                - encapsulates the whole checkout
                deletion (for expired) of process
        '''
        self.init()
        deleted_count = self.delete_expired_checkouts()
        print 'deleted %s checkout rows' %deleted_count
    
    def init(self):
        '''
            @description:
                intializes:
                    - configurations
                    - db connections
        '''
        Configuration.initialize()
        values = Configuration.values()            
        self.dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
            port=values['mysql-db']['sms_api_config']['port'],
            database=values['mysql-db']['sms_api_config']['db'],
            user=values['mysql-db']['sms_api_config']['user'],
            password=values['mysql-db']['sms_api_config']['password'])

    def delete_expired_checkouts(self):
        '''
            @description:
                - deletes the expired checkouts after
                1 week of expiration
        '''
          
        # --- logging purpose only ---
        
        ec_deleter_logger = sms_api_logger.StandAloneExpiredCheckoutDeleterLogger()             
        
        query = """select * from checkout where expired='1' 
            and (date_expiry + interval 7 day) <= now();"""       
        
        expired_checkouts = self.dbconn.run_query(query_type='select', query=query)
                
        ec_deleter_logger.info('expired checkouts to be deleted', 
            {'checkouts': str(expired_checkouts)})

        # --- start deletion ---
        
        query = """delete from checkout where expired='1' 
            and (date_expiry + interval 7 day) <= now();"""       
            
        print '\n - delete expired checkout query - \n'
        print ' '.join(query.split())
              
        try:     
            return self.dbconn.run_query(query_type='delete', query=query)
        except Exception, e:
            print e
        return None
   
def start_expired_checkout_deleter():
    '''
        @description:
            - calls ExpiredCheckoutDeleter.main()
            to process deletion of expired 
            checkouts
    '''
    cu = ExpiredCheckoutDeleter()
    cu.main()

"""
if __name__ == "__main__":
    start_expired_checkout_deleter()
"""