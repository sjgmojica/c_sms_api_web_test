import tornado.web
import inspect, sys, glob, os

import features.logging as chikka_sms_api_logger
from app.base.utils.route import route
from app.base.utils.check_connections import check_connections



class Application(tornado.web.Application):
    
    app_relative_path = 'app/web'
    
    def __init__(self, values):
        
        
        l = chikka_sms_api_logger.GeneralLogger()
        l.info('starting chikka sms api storefront web')
        
        # check necessary connections
        all_connected = check_connections(values)

        # do not load application if connections are down
        

        if all_connected :
            self.load_handlers()
            
            handlers= route.get_routes()
            
            settings = dict(
                        # this is the salt used to build cookies
                        cookie_secret='thesecretcookie',
                        
                        # this is required by tornado to determine the login page
                        login_url='/signin',
                        
                        # this is to tell tornado where the templates are (absolute path)
                        template_path=os.path.join(os.path.dirname(__file__), "%s/templates" % self.app_relative_path),
                        
                        # this is to tell tornado where the static files are (js, css etc)
                        static_path=os.path.join(os.path.dirname(__file__), "%s/static" % self.app_relative_path),
                        
                        config = values,
                        debug=True,
                        log_method=values['log_method'],
                        dragonapi_url=values['dragonpay']['payment_url']
                        
                        )

            # add special static file directory with custom handler for SVG files
            # we set the route as static-svg/(.*)
            # see ChikkaApiStaticFileHandler class definition  below
            static_svg_path=os.path.join(os.path.dirname(__file__), "%s/static_with_svg" % self.app_relative_path)
            
            handlers.append(
                            ( r"/static-svg/(.*)"  ,  ChikkaApiStaticFileHandler ,  {"path":static_svg_path}  )
                            )

        
            l.info('running web app')
            tornado.web.Application.__init__(self, handlers=handlers, reload_func=self.terminator, **settings)
        else:
            l.error('not all connections loaded, exiting app')
            raise KeyboardInterrupt()
        
    def terminator(self):
        """Terminator"""
        pass
    
    def load_handlers(self):
        handlers_dir = '%s/handlers' % self.app_relative_path
        
        module_path = self.app_relative_path.replace('/', '.') 
        
        
        # Inspect the package handlers
        for f in glob.iglob("%s/*.py" % handlers_dir):
            # Get the handler file name(w/o extension)
            filename = os.path.basename(f)[:-3] 
            # Disregard __init__ and base
            if filename not in ["__init__", "base"]:
                # Get the package's modules
                module_name = '%s.%s' % ( '%s.handlers'%module_path, filename)  
                imported = __import__('%s.handlers.%s' % ( module_path, filename), globals(), locals(), -1)



from tornado.web import StaticFileHandler

class ChikkaApiStaticFileHandler( StaticFileHandler ):


    def set_extra_headers(self, path):
        """For subclass to add extra headers to the response"""
        
        # svg files need a specific header 
        if path[-4:] == '.svg':
            self.set_header('Content-Type', 'image/svg+xml')


