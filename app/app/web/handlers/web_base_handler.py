from tornado.web import RequestHandler
from tornado.options import options

from models.account import Account
from models.session import Session
from features.shopping_cart.shopping_cart import get_cart_items_count

import utils.add_sms_credits as credit_tool


class BaseHandlerSession(RequestHandler):
    
    def __init__(self, application, request, **kwargs):
        if options.config == 'prod':
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
        
    def get_current_user(self):
        '''
        this overrides the get_current_user() of the parent.
        this is required to load user into current_user during authentication 
        
        '''
        session_id = self.get_secure_cookie('session_id', include_name=True)
        valid_account = None
        if session_id :
            # check if session exists in data store
            try :
                user_session = Session.get( session_id = session_id )
                
                if user_session : 
                    valid_account  = Account.get( account_id=user_session.account_id )
            except Exception, e :
                print 'exception raised while getting account=%s' % e
                return None
        
        if valid_account :
            try :
                valid_account.cart_count = get_cart_items_count(valid_account.account_id)
            except:
                pass
        
        return valid_account
        
        