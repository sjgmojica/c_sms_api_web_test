'''
this handler is in charge of login and logout (signin/signout)
@author: vincent agudelo
'''

from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

import features.login as login_tool
import features.registration.email as reg_email_tool
from models.session import Session

from models.account import * 

from utils.recaptcha import is_captcha_ok

@route(['/signin'])
class SigninHandler(BaseHandlerSession):
    
    def get( self ):
        '''
        this just loads the login page
        this is where the we app redirects when user is required to login
        '''
        import urllib
        import hashlib
        import time

        req_args = {}
        client_id = 'd7cb426e56af9fb398fe7bfafd823340'
        client_secret = '24be445f198fbfead22841c0749d9119'
        redirect_url = 'http://192.168.1.40:8080/signin'
        auth_url = 'https://login.mobileconnect.io/oauth2/token'

        # mobile connect provided us a code so we can fetch the authorization code
        if self.get_argument("code", ""):
          import tornado.httpclient.AsyncHTTPClient
          import base64

          req_args['grant_type'] = 'authorization_code',
          req_args['code'] = self.get_argument("code", ""),
          req_args['redirect_uri'] = redirect_url

          req = { url: auth_url,
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': len(urllib.urlencode(req_args)),
                    'Authorization': 'Bearer ' + base64.b64encode(client_id + ':' + client_secret)
                }}

          http_client = AsyncHTTPClient()
          response = http_client.fetch(req)

          print("mobile connnect auth code: %s" % response)

        else:

          # redirect the login page if MC login button is clicked
          if self.get_argument("via", "") == 'mc':
              auth_server = 'https://login.mobileconnect.io/oauth2'
              # separately join scopes since urllib.urlencode() would encode '+' as well
              scopes = '+'.join(["profile.basic.r", "profile.operator.r", "profile.msisdn.r", "profile.email.r"])
              req_args['client_id'] = client_id
              req_args['response_type'] = 'code'
              req_args['redirect_uri'] = redirect_url
              req_args['state'] = hashlib.md5(str(time.time())).hexdigest()
              req_args['acr_values'] = '2'

              redirect_url = auth_server + '?' + urllib.urlencode(req_args) + '&scope=' + scopes

              print("redirect url: %s" % redirect_url)

              self.redirect(redirect_url)
          else:
            # call get current user manually
            current_user = self.get_current_user()
            
            if current_user :
                
                next_uri = self.get_argument('next', None)              
                
                if next_uri :
                    self.redirect( next_uri )
                else:
                    self.redirect('/dashboard')
            else :
                self.render('sign_in.html')
        
        return

    def post(self):
        '''
        this method handles the submission of login
        '''
        
        username = self.get_argument('username', '')
        password = self.get_argument('password', '') 
        
        valid_user = None
        error_message = ''
        error_invalid_email = ''
        error_captcha = ''
        show_captcha = False
        
        
        if not reg_email_tool.is_email_format_valid( username ):
            error_invalid_email = 'The email address format is invalid.'

        else:
            try :
                    
                captcha_ok = False
                # in case captcha was used
                recaptcha_challenge_field = self.request.get_argument('recaptcha_challenge_field', None)
                if recaptcha_challenge_field :
                    
                    recaptcha_response_field = self.request.get_argument( 'recaptcha_response_field', None)
                    remote_ip = self.request.remote_ip
                    
                    if is_captcha_ok(
                                    recaptcha_challenge_field,
                                    recaptcha_response_field, remote_ip,
                                    self.settings['config']['recaptcha']['private_key'],
                                    self.settings['config']['recaptcha']['verify_url']):
                        
                        captcha_ok=True
                    
                    else :
                        show_captcha = True
                        error_captcha = 'The characters you entered are incorrect.'
                        raise AccountExistInvalidPassword()
                                
                valid_user = login_tool.login( email=username, password=password )
                
            except FailedLoginAttemptsExceeded, e :
                show_captcha = True
                error_message = 'You have reached the maximum number of sign in attempts.'
            
            except AccountNotExist , e :
                error_message = 'The account does not exist. <a href="/signup">Sign up now for free</a>'           
                        
            except AccountExistInvalidPassword, e :
                error_message = 'The username or password you entered is incorrect.'
                      
        if valid_user :
            try :
                # step 1 create session
                new_session = Session.new( account_id=valid_user.account_id )
                # step 2 save session to secure cookie
                self.set_secure_cookie( name='session_id', value=new_session.session_id, expires_days=2 )
                
                self.redirect('/dashboard')

            except Exception, e:
                self.redirect('/')
        else:
            if not error_invalid_email and not error_message:
                error_message = 'The username or password you entered is incorrect.'

            # check if user has failed logins
            recaptcha_public=self.settings['config']['recaptcha']['public_key']            
            
            # default page to render
            self.render('sign_in.html', error_message=error_message, show_captcha=show_captcha,
                recaptcha_public=recaptcha_public, error_invalid_email=error_invalid_email,
                error_captcha=error_captcha)
        
        return
    

@route(['/logout'])
class SignoutHandler(BaseHandlerSession):
    '''
    executes sign out
    '''
    
    def get( self ):
        
        # destroy session and redirect to signin page
        # see if session id exists in session
        session_id = self.get_secure_cookie('session_id', include_name=True)
        
        if session_id :
            # check if session exists in data store
            user_session = Session.get( session_id = session_id )
            if user_session :
                user_session.destroy()
                self.clear_all_cookies()

        self.redirect('/')
        return
