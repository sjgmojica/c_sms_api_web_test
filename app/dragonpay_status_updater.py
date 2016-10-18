'''
    @author: Jhesed Tacadena
    @description:
        - checks status of dragonpay transaction
        every x minutes (using txn_id)
        - updates neccessary DB 
        depending on status of txn
'''

from gevent.monkey import patch_all; patch_all()
from gtornado.httpclient import patch_tornado_httpclient; patch_tornado_httpclient()
from features.configuration import Configuration    
from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str) 
define("log_method", default='file', help="file | scribe | both", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
define("port", default=80, help="run on the given port", type=int)

parse_command_line()
Configuration.initialize()

import gevent
from features.payments.dragonpay.status_updater import StatusUpdater

if __name__ == '__main__':
    try:
        
        dp = StatusUpdater()
        gevent.spawn(dp.main).join()
    except Exception, e:
        import traceback
        print traceback.format_exc()