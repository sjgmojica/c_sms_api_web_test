from tornado.web import RequestHandler
from tornado.options import options
#import simplejson as json
#from pprint import pprint
#from random import randint
#from urllib import quote
#from urlparse import urlparse

#from core.models.mod_user_session import UserSession
#from core.tools.configuration import Configuration
#from models.user_publisher_session import UserPublisherSession

#from core.tools import uuid_generator 

class BaseHandlerSession(RequestHandler):
    
    def __init__(self, application, request, **kwargs):
        if options.config == 'www':
            request.add_input_header("x-scheme", "https")
        RequestHandler.__init__(self, application, request, **kwargs)
        """ 
        if self.get_argument('session_id', None):
            self._cookie_capable = False
        else:
            self._cookie_capable = self.get_cookie("_xsrf") is not None  
        
        
        if self.request.headers.has_key('User-Agent'):
            self.request.headers['user-agent'] = self.request.headers.get('User-Agent', '') 
        elif self.request.headers.has_key('user-agent'):
            pass
        else:
            self.request.headers['user-agent'] = ''
        """


#     def render( self, *args, **kwargs ):
#         
#         # do custom stuff
#         
#         
#         # call parent class
#         #print 'using override of render', dir(self)
#         
#         print 'settings',self.settings
#         print 'static url', self.static_url('css/style.css')
#         
#         
#         super(BaseHandlerSession, self).render( *args, **kwargs )



    
#     def get_current_user(self):
#         self.set_header('Cache-Control', 'must-revalidate,no-cache,no-store')
#         self.set_header('Pragma' , 'no-cache')
#         self.set_header('Expires', '-1')
#         
#         # Generate UUID for current user
#         self.session_id = self.get_secure_cookie("user_session")
#         
#         # Define the origin/source of the user who accessed this service
#         self.session_source = options.app
# 
#         # Define Configuration because sometimes config values are needed
#         # inside templates. To make it accessible, pass it to _current_user
#         conf = Configuration.config()
#         # Check session valididty
#         # ------------------------
#         # Use the core's user session creator model
#         session = UserSession()
# 
#         if (self.session_id and not session.session_exists(self.session_source, self.session_id)) or not self.session_id:
#             # At this point, the user has a stored cookie and
#             # cookie id is not in cache or current user is
#             # new to epins. In this case, session must be created
# 
#             # Recreate/create
#             self.session_id = uuid_generator.generate()
#     
#             # Sets the browser cookie
#             # Format:
#             #   user_session => < uuid >
#             self.set_secure_cookie("user_session", self.session_id, 1)
#             session.create_session(self.session_source, self.session_id, self.session_id)
# 
#         # Get the user publisher session
#         user_pub = UserPublisherSession()
#         self.publisher_session = user_pub.get_session(self.session_id)
#         
#         _current_user = {
#             "publisher_session": self.publisher_session,
#             "photo_url": conf["photo_url"]
#         }
# 
#         return _current_user
