'''
    @author: jhesed tacadena
    @year: 2013
'''
from datetime import datetime


class VerifyCodeGenerator( object ):
    
    length = 32

    @staticmethod 
    def generate_code( from_string ):
        
        import hashlib
        m = hashlib.md5()
        m.update( from_string )
        code = m.hexdigest()
        return code
    
    @staticmethod
    def is_valid_code_format(code):
        '''
        @return: Boolean . if code is not aligned with the generated code
        
        '''
        valid = False
        validchars = 'ABCDEFabcdef0123456789'
        
        if type(code) is unicode :
            code = code.encode('utf-8')
        
        if len(code) == 32 :
            
            for c in code :
                if c not in validchars :
                    #print 'invalid char [%s]' % c
                    return False
            valid = True
        
        return valid
        
    
    

class Verification(object):
    
    # static varaibles to be configured at startup
    # usage
    #  Verification.dao.function()
    #  x = Verification.expiration_length
    
    # timedelta object
    # describes duration of signupverification before it expires
    signup_verify_expiration_length = None

    # describes duration of change email verification before it expires
    change_email_verify_expiration_length = None
    
    # DAO for disk-based data (mysql)
    dao = None
    
    #dao for memory-based(redis cache) storage
    cache_dao = None
    
    verification_base_url=None
    #--- ------------------

    verification_category=None
    account_id = None
    email = None
    mobile = None
    code = None
    verification_id = None
    date_expiry=None
    
    
    max_forgot_password_send = 10

    
    def __init__(self):
        pass

     # --- SQL FUNCTIONS ---
    
    
    @staticmethod
    def get( verification_id=None, code=None, email=None, mobile=None, category=None, account_id=None, resend_code=None ):
        '''
        retrieves verification object
        @todo: make the class property accept only valid values
        '''
        
        #verifi = Verification()
        
        if code:
            # check if code uses correct format
            # for not it is the 32-character hexadecimal format
            if not VerifyCodeGenerator.is_valid_code_format( code ) :
                raise InvalidVerifyCodeFormat()
            
        elif resend_code:
            # check if code uses correct format
            # for not it is the 32-character hexadecimal format
            if not VerifyCodeGenerator.is_valid_code_format( resend_code ) :
                raise InvalidVerifyCodeFormat()
            
        
        verification_object = Verification.dao.get_verification( verification_id=verification_id, code=code, email=email, mobile=mobile, category=category, account_id=account_id, resend_code=resend_code )
        
        if verification_object :

            return verification_object
        else:
            return None

    @staticmethod
    def get_forgot_password_verify_by_code( code ):
        '''
        geets verification object for forgot password
        
        '''
        
        verification_object = Verification.dao.get_forgot_password_verifi_by_code( code = code )
        
        return verification_object
        


    @staticmethod
    def get_change_email_verification_by_code( code, resend_code  ):
        '''
        this function retrieves verification by code
        
        '''
        
        verifi = None
        
        if code :
            # check if code uses correct format
            # for not it is the 32-character hexadecimal format
            if not VerifyCodeGenerator.is_valid_code_format( code ) :
                raise InvalidVerifyCodeFormat()
                
        if resend_code :
            # check if code uses correct format
            # for not it is the 32-character hexadecimal format
            if not VerifyCodeGenerator.is_valid_code_format( resend_code ) :
                raise InvalidVerifyCodeFormat()
        
        verifi = Verification.dao.get_change_email_verification_by_code( code=code, resend_code=resend_code  )
        
        
        return verifi 
        

    def is_expired(self):
        '''
        wrapper function to determine if verification is expired
        
        '''
        expired = False
        
        #print self.date_expiry
        
        if datetime.now() > self.date_expiry :
            return True
        
        return expired
        

    def destroy(self):
        '''
        deletes the verification record
        '''
        
        Verification.dao.remove( self )
        
    def increment_resend_tries( self ):
        '''
        increments resend verification tries and returns result count
        '''
        
        resend_tries = Verification.cache_dao.increment_resend_verifi_email( self.account_id )
        
        return resend_tries
    
    @staticmethod
    def get_mobile_code(account_id, testmin):      
        return Verification.dao.get_mobile_code(
            account_id, testmin)
    
    @staticmethod
    def save_mobile_code(account_id, code, mobile):      
        return Verification.dao.save_mobile_code(
            account_id, code, mobile)
              
    @staticmethod  
    def update_mobile_code(account_id, code=None, mobile=None, ver_id=None):      
        return Verification.dao.update_mobile_code(
            account_id, code, mobile, ver_id)
    
    @staticmethod
    def delete_mobile_code(account_id, testmin):      
        return Verification.dao.delete_mobile_code(
            account_id, testmin)
              
    @staticmethod
    def get_min(account_id, verification_id):      
        return Verification.dao.get_min(
            account_id, verification_id)
              
              
    # --- REDIS FUNCTIONS ---
    
    @staticmethod
    def get_code_request_count(account_id, testmin):   
        return Verification.dao.get_code_request_count(
            account_id, testmin)
        
    @staticmethod
    def incr_code_request_count(account_id, testmin):      
        return Verification.dao.incr_code_request_count(
            account_id, testmin)

    @staticmethod
    def get_code_unverified_requests(account_id):   
        return Verification.dao.get_code_unverified_requests(
            account_id)
          
    @staticmethod
    def set_code_unverified_requests(account_id, unverified_min_list):   
        return Verification.dao.set_code_unverified_requests(
            account_id, unverified_min_list)
       
    @staticmethod
    def get_code_tries_count(account_id, testmin):   
        return Verification.dao.get_code_tries_count(
            account_id, testmin)
        
    @staticmethod
    def incr_code_tries(account_id, testmin):      
        return Verification.dao.incr_code_tries(
            account_id, testmin)

    @staticmethod
    def set_message_sent_to_pending(mobile, message_id):
        return Verification.dao.set_message_sent_to_pending(
            mobile, message_id)
            
    @staticmethod
    def set_message_sent_to_success(mobile, message_id):
        return Verification.dao.set_message_sent_to_success(
            mobile, message_id)
    
    @staticmethod
    def get_message_sent_status(mobile, message_id):
        return Verification.dao.get_message_sent_status(
            mobile, message_id)
    
    
    def add_email_to_reg_queue( self):
        '''
        adds verification to email queue
        '''
        # step 1
        # create content of verification email
        
        content = self.generate_signup_email_content()
        Verification.cache_dao.create_verification_email_content( self.verification_id, content )
        
        # step 2
        # add the email to queue (this fires the listener)
        Verification.cache_dao.add_to_signup_email_queue( verification_id=self.verification_id, email=self.email, v_type=self.verification_category )
        
        # set send status to pending
        # if redis fails in previous command, this will not be set
        Verification.set_send_status_pending( verification_id=self.verification_id)


    def add_changeemail_to_email_queue(self ):
        '''
        adds email to email queue
        
        '''
        
        content = self.generate_change_email_verify_content()
        Verification.cache_dao.create_verification_email_content( self.verification_id, content )
        Verification.cache_dao.add_change_email_to_queue( verification_id=self.verification_id, email=self.email )
        
        # set send status to pending
        # if redis fails in previous command, this will not be set
        Verification.set_send_status_pending( verification_id=self.verification_id)
        

    def add_forgot_password_email_to_queue(self):
        
        
        # step 1 generate email content
        content = self.generate_forget_password_content()

        # step 2 put content in cache
        Verification.cache_dao.create_verification_email_content( self.verification_id, content )
        
        # step 3 put password email to queue
        Verification.cache_dao.add_forgot_password_email_to_queue( verification_id=self.verification_id, email=self.email )
        # step 4 set verification status to PENDING 



    def update_forgot_password_expiry(self):
        '''
        updates password verification expiry
        
        2013-11-15 there is no official duration for expiry
        '''
        
        expiry_duration = Verification.signup_verify_expiration_length 
        self.__update_expiry(expiry_duration)
        
        
        
        

    def update_signup_expiry(self, expiry_duration=None ):
        '''
        updates expiry of signup verification by given amout or by
        amout configured in  Verification.signup_verify_expiration_length
        
        @param expiry_duration: timedelta object. duration of expiration. can be None
        @author: vincent agudelo
        
        '''
        
        if not expiry_duration :
            expiry_duration = Verification.signup_verify_expiration_length
            
        self.__update_expiry(expiry_duration)
        
        
    def update_changeemail_expiry(self):
        '''
        updates change email verification expiry
        '''
        
        self.__update_expiry( self.change_email_verify_expiration_length )
        
        
    def __update_expiry(self, expiry_duration):
        '''
        general function call to update expiry of a verification
        @param expiry_duration: timedelta object
        
        '''
        
        new_expiry_date = datetime.now() + expiry_duration
        
        Verification.dao.set_expiry_date( verification_id=self.verification_id, datetime_object=new_expiry_date )
        

    
    @staticmethod
    def create_new_signup_verification( account_id, email ):
        '''
        writes a verification record to database for account signup
        requires only the following from account save
          account_id
          email
        '''
        
        new_verification_object = None
        
        
        expiration_delta = Verification.signup_verify_expiration_length
        
        from_string = '%s%s%s' % ( email,account_id,(datetime.now() + expiration_delta ).strftime('%s')) 
        code = VerifyCodeGenerator.generate_code(from_string)
        
        resend_string = '%s%s%s' % ( account_id,(datetime.now() + expiration_delta ).strftime('%s'), email)  
        resend_code = VerifyCodeGenerator.generate_code(resend_string)

        new_verification_object = Verification.dao.create_new_signup_verification( account_id, email, code, resend_code, expiration_delta=expiration_delta )
        
        return new_verification_object


    @staticmethod
    def create_new_change_email_verification( account_object, new_email, expiration_delta ):

        verification_object = None
        
        from_string = '%s%s%s' % ( new_email,account_object.account_id,(datetime.now() + expiration_delta ).strftime('%s') )
        code = VerifyCodeGenerator.generate_code(from_string)
        
        resend_string = '%s%s%s' % ( account_object.account_id, (datetime.now() + expiration_delta ).strftime('%s'), new_email )
        resend_code = VerifyCodeGenerator.generate_code(resend_string)
       
        verification_object = Verification.dao.create_new_change_email_verification( account_object=account_object, 
            new_email=new_email, code=code, expiration_delta=expiration_delta, resend_code=resend_code )
        
        return verification_object


    @staticmethod
    def create_new_forgot_password_verification( account_object  ):
        '''
        creates a new "forgot password" verification 
        '''
        
        # increment tries for today
        tries = Verification.cache_dao.increment_forgot_password_send( account_id=account_object.account_id )
        
        if tries > Verification.max_forgot_password_send :
            raise MaxSendForgotPassword('max forgot password reached for today')

        # no formal setting for expiration of password verify
        expiration_delta = Verification.signup_verify_expiration_length
        from_string = '%s%s%s' % ( account_object.email,account_object.account_id,(datetime.now() + expiration_delta ).strftime('%s') )
        code = VerifyCodeGenerator.generate_code(from_string)
        
        resend_string = '%s%s%s' % ( account_object.account_id,
            (datetime.now() + expiration_delta ).strftime('%s'), account_object.email )
        resend_code = VerifyCodeGenerator.generate_code(resend_string)
        
        verification_object = Verification.dao.create_new_forgot_pasword_verification( 
            account_object, code, expiration_delta, resend_code  )
        
        return verification_object
        

    
    @staticmethod
    def get_existing_change_email_verification( account_id=None, email=None ):
        '''
        special function to get existing change email verification
        '''
        
        if not account_id and not email:
            raise VerificationError('missing input email=%s, account_id=%s'% (email, account_id))
        
        verification_object = Verification.dao.get_existing_change_email_verification( account_id=account_id, email=email )
        
        return verification_object
    

    @staticmethod
    def set_send_status_null( verification_id ):
        '''
        updates send status to SENT
        
        '''
        Verification.dao.set_send_status_null( verification_id=verification_id )

    
    @staticmethod
    def set_send_status_sent( verification_id ):
        '''
        updates send status to SENT
        
        '''
        Verification.dao.set_send_status_sent( verification_id=verification_id )

    @staticmethod
    def set_send_status_pending( verification_id ):
        '''
        updates send status to PENDING
        
        '''
        Verification.dao.set_send_status_pending( verification_id=verification_id )


    def generate_forget_password_content(self):
        
        
        base_url = Verification.verification_base_url
        
        url_to_click = '%s/forgotmypassword/%s' % ( base_url, self.code )
        
        content = """
        <p style="font-size:1.25em; margin-top:1em;">Please click this link to reset your password:</p>
        <div class="button" style="display:block; margin-bottom:2em;"><a href="%s" style="font-size:1.25em; display:inline-block; padding:1em; background-color:#E7604A; color:#FFFFFF; text-decoration:none; font-weight:bold;">Reset Password</a></div>
        <p style="color:#999; margin:0;">Or you can also copy  the  link below and paste it to your browser:</p>
        <p style="margin:0;"><a href="%s" style="color:#435D74;">%s</a></p>
        """ % (url_to_click, url_to_click, url_to_click)        
        
        return content

    def generate_signup_email_content(self):
        
        
        base_url = Verification.verification_base_url
        
        url_to_click = '%s/signup/verify/%s' % ( base_url, self.code )
        
        content = """
        <p style="color:#999; margin:0;">Thank you for your interest in the Chikka API</p>
        <p style="font-size:1.25em; margin-top:1em;">Please verify your email address to get started.</p>
        <div class="button" style="display:block; margin-bottom:2em;"><a href="%s" style="font-size:1.25em; display:inline-block; padding:1em; background-color:#E7604A; color:#FFFFFF; text-decoration:none; font-weight:bold;">Verify email</a></div>
        <p style="color:#999; margin:0;">Or you can also copy and paste this link to your browser</p>
        <p style="margin:0;"><a href="%s" style="color:#435D74;">%s</a></p>
        """ % (url_to_click, url_to_click, url_to_click)                
        return content
        
        
    def generate_change_email_verify_content( self ):
    
        
        base_url = Verification.verification_base_url
        
        url_to_click = '%s/changeemail/verify/%s' % (base_url, self.code)
    
        content = """
        <p style="color:#999; margin:0;">Thank you for your interest in the Chikka API</p>
        <p style="font-size:1.25em; margin-top:1em;">Please verify your email address to get started.</p>
        <div class="button" style="display:block; margin-bottom:2em;"><a href="%s" style="font-size:1.25em; display:inline-block; padding:1em; background-color:#E7604A; color:#FFFFFF; text-decoration:none; font-weight:bold;">Verify email</a></div>
        <p style="color:#999; margin:0;">Or you can also copy and paste this link to your browser</p>
        <p style="margin:0;"><a href="%s" style="color:#435D74;">%s</a></p>
        """ % (url_to_click, url_to_click, url_to_click)        
        
        return content
        
        
class VerificationError( Exception ):
    pass

class NoVerificationError( Exception ):
    pass



class VerificationExpired( Exception ):
    pass

class DuplicateVerificationCodeException(Exception):
    '''
        Custom exception triggered
        when inserting duplicate
        verification codes in table
    '''
   
    def __init__(self, suffix):
        self.code = code
    
    def __str__(self):
        return 'duplicate verification code %s' %self.code


class MaxSendForgotPassword( Exception ):
    pass



class InvalidVerifyCodeFormat( Exception ):
    pass

class ChangeEmailVerifyExists( Exception ):
    '''
    rasied when existing change email verification exists
    '''
    verification_object = None
    
    def __init__(self, verification ):
        
        self.verification_object = verification
        
    def __str__(self):
        
        msg = 'existing verification'
        if self.verification_object :
            msg = 'existing verification id=%s' % self.verification_object.verification_id
        
        return msg

