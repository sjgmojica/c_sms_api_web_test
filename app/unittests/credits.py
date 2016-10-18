from tornado.options import define, parse_command_line
from features.configuration import Configuration


import gevent
import gredis.client

import unittest

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

parse_command_line()
Configuration.initialize()


values = Configuration.values()


import utils.add_sms_credits as credit_tool

class TestRegisterUser( unittest.TestCase ) :
    
    #test_suffix = '925407'
    test_suffix = '24486'

    def setUp(self):
        pass
    
    
    def test_check_balance(self):
        
        balance = credit_tool.get_balance( self.test_suffix )
        
        print 'balance: %s' % balance
        


        

        


if __name__ == '__main__':
    
    unittest.main( verbosity=2 )