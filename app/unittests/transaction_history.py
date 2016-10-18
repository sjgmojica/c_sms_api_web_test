from gevent.monkey import patch_all
patch_all()
import gevent
from tornado.options import define, options, parse_command_line, print_help

import unittest




define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
from features.configuration import Configuration
parse_command_line()
Configuration.initialize()


from pprint import pprint

from models.transaction_history import TransactionHistory

from features.account_management import transaction_history_viewer


class TestTransactionHistory( unittest.TestCase ):
    
    def setUp(self):
        pass
    
    
    def __test_get_mo_logs(self):
        
        logs = TransactionHistory.get_mo_history()
        
        self.assertEqual(type(logs), list, 'get mo history must return a list')
    
    
    def __test_get_mt_logs(self):
        
        logs = TransactionHistory.get_mt_history()
        
        self.assertEqual(type(logs), list, 'get mt history must return a list')         
    
    
    def __test_get_latest_mo_transactions(self):
        
        transaction_history_viewer.get_latest_mo_transactions()
        

    def __test_get_latest_mt_transactions(self):
        
        transaction_history_viewer.get_latest_mt_transactions()

    def __test_get_paginated(self):
        
        
        trans = transaction_history_viewer.get_mo_paginated( 2 )
        pprint(trans) 
        
    def test_get_mt_mo_paginated_with_date(self):
        
        result = transaction_history_viewer.get_mt_paginated(
                                                    suffix='925407', 
                                                    page=1, 
                                                    m_filter=12, 
                                                    y_filter=2013, 
                                                    mobile_filter='639399239400'
                                                    )

        result = transaction_history_viewer.get_mo_paginated(
                                                    suffix='925407', 
                                                    page=1, 
                                                    m_filter=12, 
                                                    y_filter=2013, 
                                                    mobile_filter='639399239400'
                                                    )        
        

    
if __name__ == '__main__':



    
    values = Configuration.values()
    unittest.main( verbosity=2 )