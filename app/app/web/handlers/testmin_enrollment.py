from ujson import dumps
from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from models.suffixes import Suffixes
from features.testmin.testmin_enrollment import \
    process_testmin_enrollment, process_testmin_code_verification, \
    process_testmin_code_resend, has_reached_max_wrong_code_tries, \
    get_min
from utils.mobile_formatting_util import MobileNotGlobeException
from features.testmin.exceptions import *
from features.testmin.spiels import SPIELS
from utils.recaptcha import is_captcha_ok
from features.testmin.testmin_MT import *
from features.testmin.testmin_MO import *

# MAX_CODE_TRIES + 1 because redis incr starts with 1,
# and captcha should show after the MAX_CODE_TRIES + 1 (which is MAX_CODE_TRIES + 2)
# tries
MAX_CODE_TRIES = 4  

@route(['/testmin/enroll', '/testmin/enroll/'])
class TestMinEnrollRenderer(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        
        #account_obj = self.get_current_user()
        account_obj = self.current_user
        account_id = account_obj.account_id
        #testmin = get_testmin(account_id)
        testmin = account_obj.test_min

#         if account_obj.package != 'FREE':
#             self.redirect('/')
#             return
                
        # used for MO tab. this was placed in another route before.
        # but due to UI changes (which hides enroll testmin, test mt, and test mo
        # in just 1 page, it is already called here)
        
        #mo_obj = get_mo_obj(account_id)
        mo_obj = {}
        mo_obj['message'] = account_obj.test_mo_reply
        mo_obj['testmin'] = account_obj.test_min
        #if not Suffixes.has_suffix(account_id):
        #    self.redirect('/shortcode')
        #    return
        
        mo_message = mo_obj['message']
        # removes STM for display purpose
        mo_message = mo_message[len(SENT_TRIAL_MESSAGE)-2:] 
                              
        # self.render('test_receive.html', 
            # mo_message=mo_message,
            # mo_testmin=mo_obj['testmin'])
            
        self.render('verify_number_enroll.html',
            response=None, testmin=testmin, message_id=None,
            mo_message=mo_message)
            
@route(['/testmin/enroll/submit', '/testmin/enroll/submit/'])
class TestMinEnrollHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def post(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
            return
            
        # should not have default value. use JS to block
        testmin = self.get_argument('testmin', '')              
        error_message = None
        max_code_request = False
        response = {
            'error': False
        }
        
        try:
            ver_id = process_testmin_enrollment(account_id, testmin)
        except EmptyMinException, e:
            error_message = SPIELS['error11']
        except InvalidTestminException, e:
            error_message = SPIELS['error1']
        except MobileNotGlobeException, e:
            error_message = SPIELS['error12']
        except MaxUnverifiedMinEnrollmentsException, e:
            error_message = SPIELS['terror2']
        except TestminPreviouslyVerifiedException, e:
            error_message = SPIELS['error3']
        except MaxChangeMinException, e:
            error_message = SPIELS['terror4']
        except MaxCodeRequestsException, e:
            error_message = SPIELS['error5']
            max_code_request = True
        else:
            response['ver_id'] = ver_id
            response['response'] = SPIELS['success1'] % testmin[-9:]
            response['captcha'] = False
            response['recaptcha_public'] = self.settings['config']['recaptcha']['public_key']            
            response['max_code_request'] = max_code_request
            response['hide_pincode_box'] = False
            
            # self.render('pincode.html', 
                # ver_id=ver_id, response=SPIELS['success1'] % testmin[-9:], captcha=False,
                # recaptcha_public=self.settings['config']['recaptcha']['public_key'],
                # max_code_request=max_code_request, hide_pincode_box=False)
            # return
           
            self.finish(dumps(response))
                        
        if error_message:
            # self.render('verify_number_enroll.html',
                # response=error_message)
            response['error'] = True
            response['response'] = error_message
            self.finish(dumps(response))
      
            
@route(['/testmin/verify', '/testmin/verify/'])
class TestMinVerifyHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def post(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/') 
            return
        
        suffix = account_obj.suffix
        testmin = self.get_argument('testmin')
        # should not have default value. use JS to disallow it
        code = self.get_argument('code', '')
        captcha = False   
        captcha_correct = True
        max_code_request = self.get_argument('max_code_request', None)
        ver_id = self.get_argument('ver_id', None)
        recaptcha_challenge_field = self.request.get_argument(
            'recaptcha_challenge_field', None)    
        error_message = None
        try_again_tomorrow = False
        hide_pincode_box = False
        
        # print self.arguments
        
        response = {
            'error': False
        }
        
        try:
        
            # this is called here and not throwed from
            # feature as an exception because this is only
            # used for recaptcha. if an error is thrown
            # because of this, the whole process will stop
            # even though the code inputted now is correct
            
            # NOTE: this is moved here from feature to display
            # a specific spiel
            
            tries = has_reached_max_wrong_code_tries(
                account_id, testmin)
                
            if tries == int(MAX_CODE_TRIES) :
                error_message = SPIELS['error10']
                captcha = True
                                
            elif tries > int(MAX_CODE_TRIES) :

                captcha = True
                # error_message = SPIELS['error6']
                
                # -- RECAPTCHA --
            
                remote_ip = self.request.remote_ip
                recaptcha_response_field = self.request.get_argument(
                    'recaptcha_response_field', None)
                
                if is_captcha_ok(
                    recaptcha_challenge_field,
                    recaptcha_response_field, remote_ip,
                    self.settings['config']['recaptcha']['private_key'],
                    self.settings['config']['recaptcha']['verify_url']) \
                    is False and recaptcha_challenge_field:
                        response['error_captcha'] = SPIELS['recaptcha_error']
                        captcha = True
                        captcha_correct = False
                else:
                
                    process_testmin_code_verification(suffix, account_id, testmin, code)
                                    
            # --- END RECAPTCHA ---
            
            else:
                process_testmin_code_verification(suffix, account_id, testmin[-9:], code)
            
        except WrongCodeException, e:
            if not recaptcha_challenge_field and tries > int(MAX_CODE_TRIES):
                error_message = SPIELS['error5']
            elif not recaptcha_challenge_field and tries < int(MAX_CODE_TRIES):
                error_message = SPIELS['error7']
            elif recaptcha_challenge_field:
                error_message = SPIELS['error7']
            
        except ExpiredCodeMaxCodeRequestException, e:
            try_again_tomorrow = True
            error_message = SPIELS['terror9']
        except ExpiredCodeException, e:
            error_message = SPIELS['error8']
            hide_pincode_box = True

        if not error_message and captcha_correct:
            response['response'] = SPIELS['tempsuccess']
            # self.write('SUCCESSFFUL VERIFICATION')
            self.finish(dumps(response))
            return
                         
        if try_again_tomorrow:     
            response['response'] = error_message
            response['error'] = True
            
            self.finish(dumps(response))
        else:
            response['ver_id'] = ver_id
            response['testmin'] = testmin[-9:]
            response['response'] = error_message
            response['captcha'] = captcha
            response['recaptcha_public'] = self.settings['config']['recaptcha']['public_key']            
            response['max_code_request'] = max_code_request
            response['hide_pincode_box'] = hide_pincode_box
            
            if error_message:
                response['error'] = True
            
            self.finish(dumps(response))

            # self.render('pincode.html',
                # testmin=testmin[-9:], ver_id=ver_id,
                # recaptcha_public=self.settings['config']['recaptcha']['public_key'],
                # response=error_message,
                # captcha=captcha, max_code_request=max_code_request,
                # hide_pincode_box=hide_pincode_box)
 
 
@route(['/testmin/resendcode', '/testmin/resendcode/'])
class TestMinResendCodeHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
            return
            
        ver_id = self.get_argument('ver_id')
        message = ''
        testmin = None    
        captcha = False    
        response = {
            'error' : False,
            'max_code_request': False
        }
        
        try:     
            if not testmin and ver_id:
                testmin = get_min(account_id, ver_id)
            
            process_testmin_code_resend(account_id=account_id, 
                testmin=testmin, ver_id=ver_id)
            message += SPIELS['success1'] % str(testmin[-9:])
            
        except MaxCodeRequestsException, e:
            response['error'] = True
            response['max_code_request'] = True
            message = SPIELS['error5']
               
        response['response'] = message
        response['testmin'] = testmin[-9:]
        response['ver_id'] = ver_id
        response['recaptcha_public'] = self.settings['config']['recaptcha']['public_key']
        response['testmin'] = testmin[-9:]
        response['captcha'] = captcha
        response['hide_pincode_box'] = False
        
        self.finish(dumps(response))
        # self.render('pincode.html',
            # testmin=testmin[-9:], ver_id=ver_id,
            # recaptcha_public=self.settings['config']['recaptcha']['public_key'],
            # response=message,
            # captcha=captcha, max_code_request=max_code_request,
            # hide_pincode_box=False)

