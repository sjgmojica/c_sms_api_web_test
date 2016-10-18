from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

from models.session import Session
from models.account import *
from models.verification import VerificationExpired

import features.registration.registration as reg_tool
import features.registration.email_verification as email_verify_tool
import features.registration.password as password_tool

import features.registration.email as email_tool

import features.logging as sms_api_logger
from utils.html_sanitizer import sanitize_html

@route(['/signup'])
class SignupHandler(BaseHandlerSession):
    
    
    def get( self ):
        
        # call get current user manually
        current_user = self.get_current_user()
        
        if current_user :
            self.redirect('/dashboard')
        else :
            print 'default render'
            self.render('sign_up.html')
        
        return
    
    def post(self):
        
        l = sms_api_logger.GeneralLogger()
        
        l.info('attempted signup wia web', {'email':self.get_argument('email', '')})
        
        email = self.get_argument('email', '')
        
        password = self.get_argument('password', '')
        
        password_again = self.get_argument('password_again', '')
        
        response = {}
        
        # check if passwordds are the same
        error_message = ''
        error = False
            
        first_name = None
        last_name = None
        company_name = None
        address = None
         
        try :
            response = reg_tool.register_user( first_name=first_name, 
                            last_name=last_name, 
                            email=email, 
                            company_name=company_name, 
                            address=address, 
                            password=password,
                            password_again=password_again)
        
        # except password_tool.InvalidPasswordFormat, e :
            # error = True
            # error_message = 'Your password must be 8 to 32 characters with no special characters. Please check and try again.'
        
        except ActiveAccountAlreadyExisting, e :
            error = True
            error_message = 'The account already exists. To reset your password, click <a href="/forgotmypassword/">here.</a>'
            
        except PendingAccountAlreadyExisting, e :
            error = True
            error_message = 'The email address has a pending verification request. <a href="/signup/resend/%s">Click here</a> to resend verification request' % e.verification_object.resend_code
        
        # except  email_tool.InvalidEmailFormatError, e :
            # error = True
            # error_message = 'You have entered an invalid email address or password. Please check and try again.'
        
        except AccountSaveException, e :
            error = True
            print 'exception thrown while saving: %s' % e
            error_message = 'Unable to save pending account. Please try again.'
        
        except Exception , e :
            print 'random exception raised', e
            error = True
            error_message = 'Unable to register user. Please try again.'
        
        finally :
            
            inline_errors = response if (response and type(response) == dict) else {}
            
            if error or inline_errors:
                l.error('register fail')
                
                # sanitize html to avoid xss
                password = sanitize_html(password)
                password_again = sanitize_html(password_again)
                
                self.render('sign_up.html', error_message=error_message, inline_errors=inline_errors,
                    email=email, password=password, password_again=password_again)
            else:
                congrats_spiel='We sent a verification request to your email.'
                self.render('signup_email_sent.html', congrats_spiel=congrats_spiel)
    
        return
    
@route('/signup/verify/([0-9A-Fa-f]+)')
class SignupVerificationHandler( BaseHandlerSession ):
    '''
    this is the handler that accommodates the verification of account
    accepts the code in the URI
    
    code in URI shouold only be hexadecimal characters (0-9 A-F a-f)
    
    '''
    
    def get(self, code):
        
        try :
            success_account_id = email_verify_tool.verify_signup_email( code=code )
            
            if success_account_id :
                
                # auto login
                new_session = Session.new( account_id=success_account_id )
                self.set_secure_cookie( name='session_id', value=new_session.session_id, expires_days=2 )
                self.redirect('/dashboard')
                
            else :
                # verification code is invalid
                # i.e. does not exist in database
                
                error_message = 'The confirmation link is invalid. Please sign in using your email address and password.'
                # redirect to signin page
                self.render('sign_in.html', error_message=error_message)
                
        except VerificationExpired, e :
            error_message = 'The confirmation link has already expired. Click here to <a href="/signup/resend/%s">resend verification</a> request.' % code
            # expired, display resend link!
            
            resend_uri = '/signup/resend/%s' % code
            
            self.render('sign_in.html', error_message=error_message, resend_uri=resend_uri)
        except Exception, e :
            print 'failed', e
            self.redirect('/')


        
        return
        
        # process verification
        
@route('/signup/resend/([0-9A-Fa-f]+)')
class SignupResendEmail( BaseHandlerSession ):
    '''
    this handler is for resending verification link (email) in signup
    '''
    
    
    def get(self, code):
        
        try :
            result = email_verify_tool.resend_verification_email( code )
            
            
            
            
            
        except Exception, e :
            print 'exception raised', e


        if result :            
            congrats_spiel='We have sent you an email. Please check your email and confirm the link.'
            self.render('signup_email_sent.html', congrats_spiel=congrats_spiel)
            
        else:
            error_message = 'max resend reached. try again tomorrow'
            # redirect to signin page
            self.render('sign_in.html', error_message=error_message) 
        
        return
