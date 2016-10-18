from gevent.monkey import patch_all
patch_all()

import gevent
from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

from features.configuration import Configuration


parse_command_line()
Configuration.initialize()




from features.account_management.notifications import *





def main():

    # main exception handling
    import features.logging as chikka_sms_api_logger
    try:
        
        l = chikka_sms_api_logger.GeneralLogger()
        l.info('starting account notifications app')
        notif_process()
        
    except Exception, e:
        l.error('program ERROR (may need restart): %s' % e)


if __name__ == "__main__":
    gevent.spawn(main).join()
    
