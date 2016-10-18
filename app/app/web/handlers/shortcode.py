'''
    @author: Jhesed Tacadena
    @description:
        - calls shortcode feature to 
        handle generation and usage of shortcodes
        @date: 2013-10
'''

from ujson import dumps
from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from models.suffixes import DuplicateSuffixException
from features.shortcode.shortcode import process_code_list_generation,  \
    generate_shortcode, process_shortcode_claiming, account_has_shortcode, \
    is_shortcode_valid
from features.shortcode.spiels import SPIELS
from features.shortcode.exceptions import *


@route(['/shortcode', '/shortcode/'])
class ShortCodeHandler(BaseHandlerSession):
 
    @authenticated
    @asynchronous
    def get(self):
        account_id = self.get_current_user().account_id
        has_shortcode = account_has_shortcode(account_id)
        code = generate_shortcode(
            should_be_unique=True)
        self.render('shortcode.html',
            code=code, has_shortcode=has_shortcode)
              
@route(['/shortcode/search', '/shortcode/search/',
    '/shortcode/search/([\w]+)', '/shortcode/search/([\w]+)/'])
class ShortCodeListCustomHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self, custom=None):  
        self.post(custom)
    
    @asynchronous
    def post(self, custom=None):
        '''
            - ajax call
        '''
        
        if custom != 'custom':
            # used for additional spec: show only
            # clear button after user searched a code
            custom = None
        
        account_id = self.get_current_user().account_id
        starts_with = self.get_argument('starts_with', '')
        code_list = []
        error_message = None
        success_message = None
        has_shortcode = account_has_shortcode(account_id)
        
        try:
            if starts_with:
                code_list = process_code_list_generation(
                    account_id, starts_with)
            
        except ShortcodeFormatInvalidException, e:
            error_message = SPIELS['error2']
        except NoShortcodeMatchException, e:
            error_message = SPIELS['error3']
       
        # if not error_message:
            # success_message = SPIELS['tsuccess1']
               
        # data = {
            # 'code_list' : code_list,
            # 'has_shortcode' : has_shortcode,
            # 'error_message' : error_message,
            # 'starts_with' : starts_with,
            # 'success_message' : success_message
        # }
       
        if starts_with and not error_message:
            success_message = SPIELS['success2']
        
        self.render('shortcode_custom.html',
            code_list=code_list,
            has_shortcode=has_shortcode,
            error_message=error_message,
            success_message=success_message,
            starts_with=starts_with, custom=custom)
                   
@route(['/shortcode/use', '/shortcode/use/'])
class ShortCodeUseHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def post(self):
        account_obj = self.get_current_user()
        account_id = account_obj.account_id
        email = account_obj.email
        shortcode = self.get_argument('code')
        
        # used only for hackers.
        # i.e. forced their own parameter shortcode
        
        if not is_shortcode_valid(shortcode):
            self.finish(dumps({'message': 'Invalid shortcode', 'error': True}))
            return
        
        message = None
      
        try:
            process_shortcode_claiming(
                account_id, email, account_obj.package, shortcode)
            message = SPIELS['tsuccess1']
        except HasSuffixException, e:
            message = SPIELS['terror4']
        except DuplicateSuffixException, e:
            message = SPIELS['error1'] % str(shortcode)
        except Exception, e:
            error_message ='please select another short code'
   
        self.redirect('/dashboard')