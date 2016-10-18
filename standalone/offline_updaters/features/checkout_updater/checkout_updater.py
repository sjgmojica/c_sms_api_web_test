'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
        - contains functions for 
        updating checkout table
'''

from utils.configuration import Configuration
from utils.sql_tools import SQLUtils

class CheckoutUpdater(object):

    dbconn = None
    
    def main(self):
        '''
            @description:
                - encapsulates the whole checkout
                updating process
        '''
        self.init()
        # co_ids = self.get_expired_checkouts()
        updated_count = self.update_checkout_expired_field()
        print 'Updated %s checkout rows' %updated_count
    
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

    def update_checkout_expired_field(self, expired='1'):
        '''
            @description:
                - updates the column expired in checkout
                table
            @param expired (0 | 1): 
                - 0 for not expired
                - 1 for expired
            @param checkout_ids(list of dicts)
                - i.e. [{'id': 1}, {'id': 10}, {'id': 9}]
        '''
        
        # query = """update checkout set expired=%s where status = 'PENDING'
            # and expired=0 and (date_created + INTERVAL 30 MINUTE ) < now();""" % (
            # expired)
            
            
        # checkout_logger = sms_api_logger.StandAloneCheckoutUpdaterLogger() 
        
        query = """update checkout set expired=%s, date_updated=now()
            where (status IS NULL or status = 'PENDING') 
            and expired=0 and date_expiry < now();""" %(expired)

        # checkout_logger.info('updating checkout table', 
            # {'account_id': account_id, 'mobile': testmin})
            
        print '\n - update expired field in checkout table - \n'
        print ' '.join(query.split())
              
        try:     
            return self.dbconn.run_query(query_type='update', query=query)
        except Exception, e:
            print e
        return None
                        
    """     
    def get_expired_checkouts(self):
        '''
            @description:
                - returns checkout ids of expired checkouts 
                and flag 'expired' is still 0
        '''

        query =  "select id from checkout where status = 'PENDING' and expired = 0 and (date_created + INTERVAL 30 MINUTE ) < now();"
        try:
            return self.dbconn.run_query(query_type='select', query=query, 
                dictionary=False, fetchall=True)
        except Exception, e:
            print e
        return None
    """
    
def start_checkout_updater():
    '''
        @description:
            - calls CheckoutUpdater.main()
            to process checkout update
    '''
    cu = CheckoutUpdater()
    cu.main()

"""
if __name__ == "__main__":
    start_checkout_updater()
"""