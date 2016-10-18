'''
this class creates the DAO for email verification-redis

@author: email verification appends to a queue (redis list) the email to be sent

'''


from dao.redis_dao import BaseDAORedis
from features.registration.email import SendEmailError

from models.verification import VerificationError

from datetime import date, timedelta

import features.logging as sms_api_logger

class EmailVerificationRedisDAO( BaseDAORedis ):
    
    
    valid_verification_types = {
                                'signup':'SIGNUP',
                                'change_email':'CHANGEEMAIL',
                                'password':'PASSWORD',
                                'mobile':'MOBILE'
                                }
    
    signup_email_queue_key = 'smsapi_signup_email_queue'
    
    
    # max 10 sends per day
    forgot_password_send_ctr_key ='forgot_password_send_ctr:%s:%s'
    # forgot_password_send_ctr:1234:20131114
    # where
    #   1234 account id
    #   20131114 - date
    
    
    
    
    # each user is given 10 tries to resend verification email PER DAY
    signup_resed_ctr_key ='signup_resend_ctr:%s:%s'
    # i.e.
    # signup_resend_ctr:1234:20131017
    # where
    #  1234 - account id
    #  20131017 - date string ( 2013-10-17 )
    
    
    def add_to_signup_email_queue(self, verification_id, email, v_type):
        '''
        verification id  = id of verification table record
        email = email address to send to
        v_type = type of verification
        
        pushes the email value to the end of the queue
        
        '''
        
        l = sms_api_logger.GeneralLogger()
        
        l.debug('adding email to signup queue', {'email':email, 'key': self.signup_email_queue_key})
        
        queue_item = self.__build_email_queue_item(verification_id, email, v_type)
        result = self.__append_to_email_queue( queue_item )
        
        
        l.debug('added email to queue result', {'email':email, 'result':result})
        return


    def add_change_email_to_queue( self, verification_id, email ):
        '''
        adds change email to email queue
        
        '''
        
        v_type = self.valid_verification_types['change_email']
        
        queue_item = self.__build_email_queue_item(verification_id, email, v_type)
        self.__append_to_email_queue( queue_item )
        



    def add_forgot_password_email_to_queue( self, verification_id, email ):
        '''
        adds change email to email queue
        
        '''
        
        v_type = self.valid_verification_types['password']
        
        queue_item = self.__build_email_queue_item(verification_id, email, v_type)
        self.__append_to_email_queue( queue_item )



    def __append_to_email_queue(self, queue_item):
        '''
        generic fucntion to push email queue item to the queue
        '''
        
        result = None

        try :
            result = self.redis_conn.lpush( self.signup_email_queue_key, queue_item )
            
        except Exception, e :
            
            raise SendEmailError( email, 'redis query failed: %s'% e )
        
        return result


    def __build_email_queue_item(self, verification_id, email, v_type):
        '''
        format of email value to queue
          <verification_id>:<email>:<v_type>
        
        i.e.:
          123:kirby@kirby-agudelo.net:SIGNUP
        '''
        
        value = '%s:%s:%s' % (verification_id, email, v_type)
        
        return value
    

    def create_verification_email_content(self, verifi_id, content ):
        '''
        creates redis entry that stores content of email to be sent
        
        key will be in the format
          emailcontent:<vid>
        i.e:
          emailcontent:123
        
        
        the content holder of the email is TEMPORARY and no longer needed after is is sent
        aside from erasing the key after sending the email, 
        set expiration here. set to 1 hour ( 3600 seconds )
        in case something happens to the listener, the key will die in one hour
        
        
        don't worry, if the email_queue listener is alive, this will be read as soon as the email
        is queued, and may be deleted right away by the listener
        
        
        
        '''
        
        try:
            key = 'emailcontent:%s'%verifi_id
            result = self.redis_conn.setex( key, content, 3600 )
            
        except Exception, e:
            # @todo raise error here
            print 'exception rasied while writing email content to redis', e        
            pass
        
    def delete_verification_email_content(self, verifi_id ):
        '''
        this function deletes the verification email content redis entry
        
        '''

        pass



    def increment_forgot_password_send(self, account_id ):
        
        try:
            datetoday = date.today()
            key = self.forgot_password_send_ctr_key % (account_id, datetoday.strftime('%Y%m%d'))
            new_value = self.redis_conn.incr( key )
            if new_value == 1 :
                # set expiration to 1 day
                self.redis_conn.expireat( key,  (datetoday+timedelta(days=1)).strftime("%s")    )
            
        except:
            raise VerificationError('unable to increment password send')
        else :
            return new_value


    def increment_resend_verifi_email(self, account_id ):
        '''
        increments the resend counter for each user 
        this is for each day only
        '''
        
        try :
            datetoday = date.today()
            key = self.signup_resed_ctr_key % (account_id, datetoday.strftime('%Y%m%d'))
            new_value = self.redis_conn.incr( key )
            
            if new_value == 1:
                # this is the first time that this was created
                # set expiration
                self.redis_conn.expireat( key,  (datetoday+timedelta(days=1)).strftime("%s")    )
            
        except Exception, e :
            raise VerificationError('unable to increment resend counter for account id %s; ' % account_id)
        
        else :
            
            return new_value
        