from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


parse_command_line()
Configuration.initialize()

values = Configuration.values()



from utils.mobile_formatting_util import is_mobile_format_valid


if __name__ == '__main__':
    
    print 'start test'
    
    
    base='4296705'
    
    mobile = '09474296705'
    
    
    
    cases = [
             (  '0947%s'%base, True),
             ('+63947%s'%base, True), 
             ( '63947%s'%base, True),
             (   '947%s'%base, True),
             ('1111', False), # too short
             ('123123123123123', False) # too long
             ]
    
    for test_item in cases :
        
        mobile = test_item[0]
        will_assert =  test_item[1]
        
        result =  is_mobile_format_valid( mobile=mobile )
        #print result
        if result is will_assert:
            print 'passed ->', mobile
        else:
            print 'failed->', mobile
          
    