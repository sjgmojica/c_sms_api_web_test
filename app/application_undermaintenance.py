import os.path
import tornado.web
from tornado.options import options
from app.web.handlers.web_base_handler import BaseHandlerSession
 
class UnderMaintenanceHandler(BaseHandlerSession):
    def get(self): 
        self.render('undermaintenance.html')

class ApplicationUnderMaintenance(tornado.web.Application):
    
    app_relative_path = 'app/web'
    
    def __init__(self, values):   
        
        handlers = []
        handlers.append(("/", UnderMaintenanceHandler))
        handlers.append(("/[A-Za-z0-9-]+[ 0-9A-Za-z#$%=,`~&*()'?.:;_|^/+-]*", 
            UnderMaintenanceHandler))        
        settings = dict(
        
            cookie_secret='thesecretcookie',
            template_path=os.path.join(os.path.dirname(__file__),
                                       "%s/templates" % self.app_relative_path),
            static_path=os.path.join(os.path.dirname(__file__), 
                "%s/static" % self.app_relative_path),
                    
            debug=False,
            log_method=options.log_method
        )
        tornado.web.Application.__init__(self, handlers=handlers,
                                         reload_func=self.terminator,
                                         **settings)

    def terminator(self):
        print "terminated"