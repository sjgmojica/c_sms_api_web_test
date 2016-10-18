import gevent
from gevent.monkey import patch_all
patch_all()
from gtornado.httpclient import patch_tornado_httpclient
patch_tornado_httpclient()

from gtornado.httpserver import patch_tornado_httpserver
patch_tornado_httpserver()

from gtornado.ioloop import patch_tornado_ioloop
patch_tornado_ioloop()

from gtornado.ioloop import GIOLoop
from gtornado.httpserver import GHTTPServer

from gtornado.web import patch_tornado_web
patch_tornado_web()

from tornado.options import define, options, parse_command_line, print_help

from features.configuration import Configuration
import os

define("app", default='web', help="web | undermaintenance", type=str) 
define("config", default='debug', help="run configuration settings", type=str) 
define("log_method", default='file', help="file | scribe | both", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
define("port", default=80, help="run on the given port", type=int)

#--- declare apps

def web( *args, **kwargs ):
    
    
    configuration = { 'log_method' : 'file'}
    configuration.update( Configuration.values() )
    
    from application import Application
    return Application( configuration )
    
    
def undermaintenance( *args, **kwargs ):    
    configuration = { 'log_method' : 'file'}
    configuration.update( Configuration.values() )
    
    from application_undermaintenance import ApplicationUnderMaintenance
    return ApplicationUnderMaintenance( configuration )



application_factory = {
    "web": web,
    "undermaintenance": undermaintenance,
    #"static": static,
    #"mobile": mobile
}




def main():
    
    try:
        
        
        parse_command_line()
        Configuration.initialize()
        import features.logging as chikka_sms_api_logger
        l = chikka_sms_api_logger.GeneralLogger()
        
        app_type = options.app
        port = options.port
        debug = True
        

        if debug:
            print "[!!!DEBUG MODE!!!]"
            bind_to_cpu = -2

        log_method='file'
        scribe_host=None
        scribe_port = 1234
        category = 'smsapi_access'
        server_ip = '10.11.2.225'

        app = application_factory[app_type]



        ghttp_args = {
                      "port": port,
                      "bind_to_cpu": int(bind_to_cpu)
                      }


        l.info('running gtornado at %s/%s' %  ( os.path.dirname(os.path.realpath(__file__)), __file__ ), { 'settings': ghttp_args} )

        if options.config != 'prod':
            ghttp_args['log_method'] = 'file'

        
        http_server = GHTTPServer(app, **ghttp_args )
        
        #start the server
        http_server.start()
        GIOLoop.instance().start()
        
        
        
    except KeyboardInterrupt:
        
        pass
    
#    except Exception, e :
#        print 'exception raised', e



if __name__ == "__main__":
    main()
