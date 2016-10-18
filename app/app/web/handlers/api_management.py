'''
    @author: Jhesed Tacadena
    @description:
        - manages API settings
        @date: 2013-10
'''

from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from features.api_management.api_management import process_api_update, \
    get_content_provider_obj, validate_rsa_signature
from features.api_management.exceptions import *
from features.api_management.spiels import SPIELS
from ujson import dumps
from utils.html_sanitizer import sanitize_html

@route(['/api/settings', '/api/settings/',
    '/api/settings/([\w]+)', '/api/settings/([\w]+)/'])
class ApiSettingsHandler(BaseHandlerSession):
 
    @authenticated
    @asynchronous
    def get(self, success_message=None):
    
        if success_message == 'success':
            success_message = SPIELS['success1']
            
        account_obj = self.get_current_user()
        if not account_obj.suffix:
            #self.redirect('/shortcode')
            cp_obj=None
        else:
            cp_obj = get_content_provider_obj(account_obj)
            
               
        self.render('api_settings.html', cp_obj=cp_obj,
            success_message=success_message)
    
    @authenticated
    @asynchronous
    def post(self):
        '''
            @description:
                - handles editing of API update
                - not following 'try except format'
                because it is being called using ajax
                (see main.js -> Model -> apiSettingsEdit)
        '''
        
        account_obj = self.get_current_user()
        if not account_obj.suffix:
            self.redirect('/shortcode')
            
        public_key = self.get_argument('public_key', ' ')
        callback_url = self.get_argument('callback_url', ' ')
        mo_url = self.get_argument('mo_url', ' ')
        error_messages = None
        
        
        try:
            public_key = sanitize_html(public_key)
            callback_url = sanitize_html(callback_url)
            mo_url = sanitize_html(mo_url)
            
            error_messages = process_api_update(account_obj, public_key,
                    callback_url, mo_url)
        except Exception, e:
            print e
                    
        self.finish(dumps(error_messages))
        
@route(['/api/settings/publickey/verify', '/api/settings/publickey/verify/'])
class VerifyPublicKey(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def post(self):

        account_obj = self.get_current_user()
        if not account_obj.suffix:
            self.redirect('/shortcode')
            
        rsa_message = self.get_argument('rsa_message')
        # rsa_message = 'Hello'
        rsa_signature = self.get_argument('rsa_signature', None)
        
        message = validate_rsa_signature(account_obj.suffix,
            rsa_message, rsa_signature)
        
        self.finish(dumps(message))
    
@route('/secret-key-(generate|retrieve)')
class GenerateSecretKey( BaseHandlerSession ):
    
    @authenticated
    @asynchronous    
    def get(self, key_method):
        '''
        signal will be called via ajax request.
        this will automatically create the secret key no matter what
        
        '''
        
        account_obj = self.get_current_user()
        
        return_value = '{"secretkey": null }' 
        
        try:
            secret_key = account_obj.generate_secret_key()
            return_value = '{"secretkey":"%s"}' % secret_key
        
        except Exception, e:
            print 'exception raasied while generating secret key'
        
        self.finish( return_value )