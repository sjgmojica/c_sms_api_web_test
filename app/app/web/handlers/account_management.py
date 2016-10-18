from tornado.web import authenticated, asynchronous
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

import ujson as json 
import features.registration.change_email as change_email_tool


from models.account import ActiveAccountAlreadyExisting, PendingAccountAlreadyExisting, SameEmailError, Account, SameToOldPassword, AccountSaveException
from models.verification import ChangeEmailVerifyExists, VerificationExpired

from models.session import Session


from features.account_management import password as edit_passwsord_tool
from features.account_management.password import password_tool, spiels as change_password_spiels
from features.account_management.update_profile import update_profile, update_name,change_billing_email
from utils.html_sanitizer import sanitize_html

from pprint import pprint


import features.logging as sms_api_logger_tool


from features.account_management.balance_notif_main import enable_balance_notification, disable_balance_notification, update_balance_threshold



@route('/changeemail')
class ChangeEmailHandler( BaseHandlerSession ):
    
    @authenticated
    def get(self):
        
        self.render('change_email.html')
        return
    
    @authenticated
    def post(self):
        
        new_email = self.get_argument('new_email', None)
        error_message = ''
        
        
        error = False
        try :
        
            change_email_tool.change_email( account_object=self.current_user, new_email=new_email )
        
        except (ActiveAccountAlreadyExisting, PendingAccountAlreadyExisting) as e :
            error_message = 'You have entered an invalid email address. Please check and try again.'
            error = True

        except ChangeEmailVerifyExists, e :
            error = True
            mail_spiel = 'The email address has a pending verification request.'
            
            error_message = '%s <a href="/changeemail/verify/resend/%s">Click here</a> to resend verification request.' % (mail_spiel, e.verification_object.code)
            
        except SameEmailError, e :
            error_message = 'The email address is already registered.'
            error = True
        finally:
        
            if error :
                self.render('change_email.html', error_message=error_message)
            else:
                # get template for success
                self.render('change_email_email_sent.html')
        
        return
    
@route('/ajax/changeemail')
class ChangeEmailAjax( BaseHandlerSession ):
    '''
    ajax response handler
    '''
    @authenticated
    def post(self):
        
        logger = sms_api_logger_tool.GeneralLogger()

        new_email = self.get_argument('new_email', None)
        logger.info('received request to change email', {'account_id':self.current_user.account_id, 'new_email':new_email})
        
        error_message = ''
        
        success = False
        success_message = ''
        try :
        
            change_email_tool.change_email( account_object=self.current_user, new_email=new_email )
            success = True
            
            success_message = 'We sent a verification request to your email.'
        
        except PendingAccountAlreadyExisting, e :
            
            if e.verification_object:
                error_message = 'The email address has a pending verification request. <a href="/signup/resend/%s">Click here</a> to resend verification request' % e.verification_object.code
            else:
                error_message = 'The email address has a pending verification request.'
            success = False
            
        except (change_email_tool.InvalidEmailFormatError) as e :
            error_message = 'The email address format is invalid.'
            logger.error('email has an invalid format', {'exception_msg': str(e)})
            success = False

        except (ActiveAccountAlreadyExisting) as e :
            error_message = 'The email address format is invalid.'
            logger.error('email used is already existing / being used', {'exception_msg': str(e)})
            success = False
            
        except ChangeEmailVerifyExists, e :
            success = False
            mail_spiel = 'The email address has a pending verification request.'
            
            error_message = '%s <a href="#" onClick="change_email_ajax_resend( \'%s\' ); return false">Click here</a> to resend verification request.' % (mail_spiel, e.verification_object.resend_code)
            #error_message = '%s Click here to resend verification request.' % (mail_spiel, e.verification_object.code)
            attachment_uri = "/changeemail/verify/resend/%s" % e.verification_object.code
            
            
            logger.error('email has an existing verify request', {'exception_msg': str(e)})
            
        except SameEmailError, e :
            error_message = 'The email address is already registered.'
            success = False
            
            logger.error('same as current email / username', {'exception_msg': str(e)})
            

        except Exception , e :
            logger.error('uncaught exception', {'exception_msg': str(e)})
            error_message = 'unexpected error. please reload the page and try again'
            success = False
            
            
        finally:
        
            response = {'success' : success,  
                        'error_message': error_message ,
                        'success_message' : success_message
                        }
            
            # output json response
            self.write( json.dumps(response) )

        logger.info('done with change email request')


@route('/changeemail/verify/([0-9a-zA-z]+)')
class VerifyChangeEmailHandler( BaseHandlerSession ):
    '''
    receives the verification URL that will execute change email
    
    '''
    
    def get(self, code):
        
        
        logger = sms_api_logger_tool.GeneralLogger()
        
        error_message = ''
        
        
        # step 1
        # verify change email
        error = False
        error_message = ''
        success_message = ''
        
        try :
            logger.info('received change email verify from web', data=code)
            
            change_email_tool.verify_change_email( code=code )
            
        except VerificationExpired, e    :
            
            main_spiel = 'The confirmation link has already expired'
            
            logger.error( 'attempted to use expired verification code' , data=code)
            
            error_message='%s. <a href="/changeemail/verify/resend/%s">Click here</a> to resend verification request.' % ( main_spiel, code )

        except change_email_tool.InvalidVerifyCodeFormat, e :
            error_message = 'The confirmation link is invalid.'
            logger.error( 'attempted to use invalid format for code' , data=code)
        
        except change_email_tool.NoVerificationError, e :

            
            logger.error( 'attempted to use non existing email verification code' , data=code)
            
            error_message = 'The confirmation link is invalid. Please sign in using your email address and password.'

        
        except Exception, e :
            error_message = 'an error occured. please try again later'
            logger.error('unexpected error raised', data=e)
        
        finally :
            # force logout
            
            # delete all cache
            session_id = self.get_secure_cookie('session_id', include_name=True)
            if session_id :
                user_session = Session.get( session_id = session_id )
                if user_session :
                    user_session.destroy()
                
            self.clear_all_cookies()
            
            if not error_message:
                success_message = 'You have successfully updated your email address. You may now sign in using your new email address.'
            self.render('sign_in.html', error_message=error_message, success_message=success_message)
        
            logger.info('change email verify done', data=code)
        
        
        
@route('/changeemail/verify/resend/([0-9A-Fa-f]+)')
class VerifyChangeEmailHandler( BaseHandlerSession ):
        
        
    def get(self, code):
        
        try:
            change_email_tool.resend_change_email_verify( code )
        except Exception, e:
            logger = sms_api_logger_tool.GeneralLogger()
            logger.info('change email resend verification failed', 
                data={'code': code})
        
        congrats_spiel='We have sent you an email. Please check your email and confirm the link.'
        self.render('signup_email_sent.html', congrats_spiel=congrats_spiel)
        



@route('/changeemail/verify/ajax-resend/([0-9A-Fa-f]+)')
class VerifyChangeEmailHandler( BaseHandlerSession ):
        
    @authenticated
    def get(self, code):
        
        response = { 'success':False }
        
        
        try:
            change_email_tool.resend_change_email_verify( code )
            response['success'] = True
            response['success_message'] = 'We have sent you an email. Please check your email and confirm the link.'
        except Exception, e :
            print 'resend failed %s' % e
            import traceback
            print traceback.format_exc()
            response['error_message'] = 'invalid code'
            
        self.write( json.dumps(response) )
        

        
        
        
        
        
@route(['/account/settings/view/([\w]+)', '/account/settings/view/([\w]+)/', 
    '/account/settings/view', '/account/settings/view/'])
class ViewAccountSettingsRenderer(BaseHandlerSession):
    '''
        @description:
            - renders the account settings page
        @author: Jhesed Tacadena
    '''
    @asynchronous
    @authenticated
    def get(self, success_message=None):
    
        # success_message is passed in URL using ajax call
        # this was implemented this way to avoid creating
        # a new JS code view for rendering account settings
        if success_message:
            success_message = 'You have successfully updated your account information.'
            
        account_obj = self.get_current_user()
        self.render('account_settings.html', 
            account_obj=account_obj,
            success_message=success_message,
            notification_message=None,
            balance_notification_enabled = account_obj.balance_notif_enabled,
            balance_notif_threshold = account_obj.balance_notif_threshold
            
            )
            
                
@route(['/account/settings/change', '/account/settings/change/'])
class ViewAccountSettingsRenderer(BaseHandlerSession):
    '''
        @description:
            - renders the account settings page
        @author: Jhesed Tacadena
    '''
    @asynchronous
    @authenticated
    def get(self):
        account_obj = self.get_current_user()
        self.render('edit_name_address.html', 
            account_obj=account_obj)
    
    @asynchronous
    @authenticated
    def post(self):

        account_obj = self.get_current_user()
        firstname = self.get_argument('firstname', ' ')
        lastname = self.get_argument('lastname', ' ')
        address = self.get_argument('address', ' ')
        company = self.get_argument('company', ' ')
        
        firstname = firstname.encode('utf-8') 
        lastname = lastname.encode('utf-8') 
        address = address.encode('utf-8') 
        company = company.encode('utf-8') 
                
        # updates API settings based on user input
        
        try:
            update_profile(account_obj.account_id, firstname, 
                lastname, address, company)
            account_obj = self.get_current_user() # for updating profile on the fly
        except Exception, e:
            import traceback
            print traceback.format_exc()
            
        self.finish(json.dumps({'message': 'success'}))
        # self.render('account_settings.html', 
            # account_obj=account_obj,
            # success_message='[temp] Profile successfully updated.',
            # notification_message=None)  # for future use only)
        

    
    
@route(['/edit/password', '/edit/password/'])
class ChangePasswordHandler( BaseHandlerSession ):
    '''
    handler for edit password via web
    @author: vincent agudelo
    
    '''
    
    @authenticated
    def get(self):
        
        self.render('change_password.html')
        return
        
        
        
    def post(self):

        # initialize default var values
        error_message = ''
        error = False

        # get parameters from input
        # don't worry , it is safe to pass to the feature, there is checking there
        old_password = self.get_argument('old_password','')
        new_password = self.get_argument('new_password','')
        
        
        try :
            result = edit_passwsord_tool.edit_password( self.current_user.account_id, old_password, new_password )
        except password_tool.InvalidPasswordFormat, e:
            error = True
            error_message = change_password_spiels['invalid_format']

        except password_tool.InvalidPasswordLength, e:
            error = True
            error_message = change_password_spiels['invalid_password_length']
        
        except edit_passwsord_tool.InvalidOldPassword ,e :
            error = True
            error_message = change_password_spiels['invalid_old_password']
        
        except Exception, e:
            print e
            error = True
            error_message = 'unexpected error, please try again'
        else:
            error_message = 'password successfully changed'
                    
        finally:
            self.render('change_password.html', error_message = error_message)
        
        
        return



@route(['/ajax/edit_password', '/ajax/edit_password/'])
class changePasswordAjaxHandler( BaseHandlerSession ):
    
    def post(self):
        
        old_password = self.get_argument('old_password', '')
        new_password = self.get_argument('new_password', '')
        new_password_again = self.get_argument('new_password_again', '')
        
        response = {'success' : False ,  
                    'success_message' : '',
                    'old_password_error': '' ,     
                    'new_password_error':'',
                    'new_password_again_error':'',
                    'general_error' :
                    'error occured'}
        
        

        if not old_password:
            response['old_password_error'] = "You can't leave this empty."
         
        if not new_password:
            response['new_password_error'] = "You can't leave this empty."
         
        if not new_password_again:
            response['new_password_again_error'] = "You can't leave this empty."
         
         
        if not response['old_password_error'] and not response['new_password_error'] and not response['new_password_again_error']:
           
            if new_password_again == new_password :
                                
                try :
                    result = edit_passwsord_tool.edit_password( self.current_user.account_id, old_password, new_password )
                except password_tool.InvalidPasswordFormat, e:
                    print e
                    response['success'] = False
                    response['new_password_error'] = change_password_spiels['invalid_format']
        
                except password_tool.InvalidPasswordLength, e:
                    print e
                    response['success'] = False
                    response['new_password_error'] = change_password_spiels['invalid_password_length']
                except edit_passwsord_tool.InvalidOldPassword ,e :
                    print e
                    response['success'] = False
                    response['old_password_error'] = change_password_spiels['invalid_old_password']
                except SameToOldPassword, e :
                    print e
                    response['success'] = False
                    response['new_password_error'] = 'Your new password should be different from your old password.'
              
                except Exception, e:
                    
                    response['success'] = False
                    error = True
                    print 'exception rasied: %s' % e
                    response['general_error'] = 'unexpected error, please try again' 
                     
                else:
                    response['success'] = True
                    response['success_message'] = 'password successfully changed'
                            
            else:
                
                response['success'] = False
                response['new_password_error'] = change_password_spiels['not_match']
                
        self.write( json.dumps(response) )


@route(['/forgotmypassword', '/forgotmypassword/([a-fA-F0-9]+)?'])
class ForgotaPasswordHandler( BaseHandlerSession ):
    
    def get(self, code=None):
        '''
        default page for forgert password secquence
        accepts 32character MD5 code for forget password
        '''
        
        error_message = ''
        error = False
        
        if code is None :
            self.render('forgot_password.html')
            
        else:
            
            code_valid = False
            try :
                code_valid = edit_passwsord_tool.is_valid_forget_password_code( code=code )

            
            except edit_passwsord_tool.VerificationExpired, e :
                error_message = 'Your password link is invalid. Click <a href="/forgotpassword">here</a> to resend another password link.'
                self.render('forgot_password.html', error_message=error_message)
                
                
            except Exception, e:
                error_message = 'unexpected error. please try again.'
                
                print 'exception thrown', e
                self.render('forgot_password.html', error_message=error_message)
                
            else:
            
                if code_valid is False :
                    error_message = change_password_spiels['invalid_code']
                    self.render('forgot_password.html', error_message=error_message)
                else:
                    self.render('change_password_frm_forgot.html', code=code)

        
    def post(self, code=None):
        
        email = self.get_argument('email', None)
        error_message = ''
        success_message = ''
        if email :
            
            
            template_vars = {}
            
            
            try :
                edit_passwsord_tool.forgot_password_send( email=email )
                
                
                success_message = edit_passwsord_tool.spiels['email_sent']  # 'We sent a verification request to your email'
                
                template_vars['success_message'] = success_message

            except (  edit_passwsord_tool.PendingAccountAlreadyExisting    , edit_passwsord_tool.AccountNotExist , edit_passwsord_tool.InvalidEmailFormatError), e :
                
                
                error_message = 'The email address is either invalid or unregistered.'
        
                template_vars['error_message'] = error_message
                
            except edit_passwsord_tool.MaxSendForgotPassword, e :
                template_vars['error_message'] = 'You have reached the maximum number of password reset request.'
                
                
            except Exception, e :
                
                print 'unexpected error : %s' % e
                template_vars['error_message'] = 'unexpected error. please try again'
        
            finally :
                
                self.render('forgot_password.html', **template_vars)
        elif code:
            
            new_password = self.get_argument('new_password', None)
            new_password_again = self.get_argument('new_password_again', None)
            
            if new_password is not None and new_password_again is not None and new_password == new_password_again:
            
                template_vars = {}
            
                try :
                    result = edit_passwsord_tool.change_password_by_code( code, new_password )
                    
                    if result :
                        template_vars['success_message'] = 'You have successfully changed your password.'
                        
                    else :
                        self.redirect('/forgotmypassword/%s'%code)
                except password_tool.InvalidPasswordFormat:
                    template_vars['error_message'] = change_password_spiels['invalid_format']
                    
                finally :
                    self.render('change_password_frm_forgot.html', code=code, **template_vars )
                    
                    
            else :
                error_message = change_password_spiels['not_match']
                self.render('change_password_frm_forgot.html', code=code, error_message=error_message)
                
        else:
            error_message='You have entered an invalid email address. Please check and try again.'
            self.render('forgot_password.html', error_message=error_message)
            

@route(['/forgotmypassword/resend/([a-fA-F0-9]+)?'])
class ForgotaPasswordHandler( BaseHandlerSession ):
    
    def get(self, code ):
        
        error_message = ''
        success_message = ''
        
        try :
            
            edit_passwsord_tool.resend_forgot_password_by_code( code = code )
            
            
            success_message = edit_passwsord_tool.spiels['email_sent']
        
        except edit_passwsord_tool.VerificationError , e :
            
            error_message= edit_passwsord_tool.spiels['invalid_code']
        
        except Exception, e :
            print 'exception thrown: %s' % e
            error_message= 'error occured, please try again'
            
        
        self.render('forgot_password.html', error_message=error_message, success_message= success_message )


@route( '/billing-settlement' )
class BillingAndSettlement( BaseHandlerSession ):

    @asynchronous
    @authenticated    
    def get(self):
        
        self.render('billing_settlement.html')


@route( '/ajax/change-name' )
class ChangeNameHandler( BaseHandlerSession ):
    
    @asynchronous
    @authenticated
    def post(self):
        '''
        receives name from subited form and saves it to database
        '''

        logger = sms_api_logger_tool.GeneralLogger()
        name = self.get_argument('new_name', None)
        logger.info('received ajax request to change complete name / company name', data={'account_id': self.current_user.account_id, 'original_name':self.current_user.name, 'new_name':name})

        
        
        try:
            update_name( account_object=self.current_user, name=name )
            response = {'result':True}
        except Exception, e:
            print 'unable to update name'
        
            response = {'result':False}
            logger.error('error in changing name', data=e)
        
        logger.info('request done')
        
        self.finish( json.dumps(response) )
        
@route( '/ajax/change-billing-email' )        
class ChangeBillingEmailAjax( BaseHandlerSession ):

    @asynchronous
    @authenticated
    def post(self):
        
        
        logger = sms_api_logger_tool.GeneralLogger()
        logger.info(message='received change billing email request', data={'account_id':self.current_user.account_id, 'new email':self.get_argument('new_email', None), 'old_email': self.current_user.billing_email })
        
        success_message = ''
        default_error_message = 'unable to save billing email. Please try again'
        error_message = ''
        
        final_result= False
        
        try:
        
            result = change_billing_email( self.current_user, self.get_argument('new_email', None) )
            if result :
                logger.info(message='successful change')
                success_message = 'billing email updated'
                final_result = True
            else:
                logger.error(message='invalid email format')
                error_message = 'invalid email'

        except AccountSaveException, e:
            
            error_message = default_error_message
            logger.error(message='could not save data', data=e)
            
        except Exception, e:
            error_message = default_error_message
            logger.error(message='unknown error occurred', data=e)
            
            
        
        response = {'success': final_result, 'error_message':error_message, 'success_message':success_message }
        
        self.finish( json.dumps(response) )
        logger.info(message='request handling finished')
        
@route( '/ajax/balance-notif/(enable|disable)' )
class BalanceNotifEnableHandlerAjax( BaseHandlerSession ):

    @asynchronous
    @authenticated    
    def post(self, enable_disable):
        logger = sms_api_logger_tool.GeneralLogger()
        user = self.current_user
        try:
            if 'enable' == enable_disable:
                user.enable_balance_notification()
                logger.info('enable balance threshold notification', { 'account_id':user.account_id    }    )
                
            elif 'disable' == enable_disable:
                user.disable_balance_notification()
                logger.info('disable balance threshold notification', { 'account_id':user.account_id    }    )
            else:
                print 'invalid input'
        except Exception, e :
            logger.error('enable/disable balance notif unexpected error: %s' % e, { 'type' : enable_disable , 'account_id':user.account_id    }    )
            self.write( json.dumps( {'result': False} )   )
        else:

            self.write( json.dumps( {'result': True} )   )
        self.finish()

@route( '/ajax/update-balance-threshold' )
class UpdateBalanceThresholdHandlerAjax( BaseHandlerSession ):
    
    @asynchronous
    @authenticated    
    def post(self):
        '''
        handles request to update balance threshold value
        all errors are thrown as an exception and result=False is returned iin JSON format
        if successful result=True is returned
        
        '''
        
        new_threshold = self.get_argument('new_threshold', None)
        logger = sms_api_logger_tool.GeneralLogger()
        user = self.current_user
        
        try:
            old_threshold = user.balance_notif_threshold
            update_balance_threshold( account_object=user, threshold=new_threshold )
            logger.info('updated balance threshold', {'account_id':user.account_id,  'old_threshold': old_threshold ,    'new_threshold':new_threshold})
        except Exception, e:
            logger.error('update balance threshold. unexpected error: %s' % e, {'account_id':user.account_id } )
            self.write(  json.dumps( {'result': False} ) )            
        else:
            self.write(  json.dumps( {'result': True} ) )
        self.finish()