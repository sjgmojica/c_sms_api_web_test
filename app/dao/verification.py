'''
    @author: jhesed tacadena
    @year: 2013
'''

from ujson import dumps
from datetime import datetime, timedelta
from models.verification import Verification, VerificationError


KEY_CODE_REQUEST_CTR = 'code:request:user:%s:testmin:%s'
KEY_CODE_UNVERIFIED_REQUEST_CTR = 'testmin:unverified:user:%s'
KEY_CODE_TRIES_CTR = 'code:tries:user:%s:testmin:%s'
KEY_CODE_REQUEST_EXPIRATION = 900 # 15 min

KEY_MESSAGE_SENT_FLAG = 'mid:%s:%s:status'
KEY_MESSAGE_SENT_FLAG_EXPIRATION = 900 # 15 min
EXPIRATION_PINCODE = 6 # hours

class VerificationDao(object):
    
    # mapping of the valid status in databse table `verification`
    valid_categories = {
                        'signup':'SIGNUP',
                        'change_email':'CHANGEEMAIL',
                        'password':'PASSWORD',
                        'mobile':'MOBILE'
                        }
    
    valid_send_status = {'sent':'SENT', 'pending':'PENDING'}
    
    
    
    def __init__(self, dbconn, redisconn=None):
        self.dbconn = dbconn
        self.redisconn = redisconn
        
    # --- SQL FUNCTIONS ---

    def remove(self, verification_object):
        
        criteria = {
                    'id' : verification_object.verification_id
                    }
        
        try :
            
            self.dbconn.execute_delete(
                table_name='verification', 
                conditions=criteria, 
                operator='AND')
            
            
        except Exception ,e :
            
            raise VerificationError('unable to delete verification id:%s ; %s' % (verification_object.verification_id, e))
        
        

    def set_expiry_date(self, verification_id, datetime_object ):
        '''
        sets the expiration date of a verification
        used in updating expiry
        '''

        params = {
                  'date_expiry' : datetime_object.strftime('%Y-%m-%d %H:%M:%H')
                  }
        
        conditions = {'id':verification_id}
        
        self.__update_record(params, conditions)
        

    def set_send_status_null(self, verification_id ):
        '''
        updates send_status field in verification table to sent
        
        '''
        
        send_status = self.valid_send_status['sent']
        
        params = {'send_status' : None}
        conditions = { 'id' : verification_id }
        
        self.__update_record(params, conditions)
        
    def set_send_status_sent(self, verification_id ):
        '''
        updates send_status field in verification table to sent
        
        '''
        
        send_status = self.valid_send_status['sent']
        
        params = {'send_status' : send_status}
        conditions = { 'id' : verification_id }
        
        self.__update_record(params, conditions)
        
        
    def set_send_status_pending(self, verification_id ):
        '''
        updates send_status field in verification table to sent
        
        '''
        
        send_status = self.valid_send_status['pending']
        
        params = {'send_status' : send_status}
        conditions = { 'id' : verification_id }
        
        self.__update_record(params, conditions)        
        


        
    def __update_record( self, params, conditions ):
        '''
        updates verification table
        
        '''

        try :
            self.dbconn.execute_update(
                table_name='verification', params=params,
                operator='AND', conditions=conditions)
        except Exception, e:
            raise VerificationError('unable to write to email queue: %s' % e)
            



    def get_verification(self, verification_id=None, code=None, email=None, mobile=None, category=None, account_id=None, resend_code=None ):
        '''
        retrieves verification information based on information in given object
        
        '''
        verification_object = None
        
        criteria = {}
        
        if verification_id :
            criteria['id'] = verification_id
        
        if code :
            criteria['code'] = code

        if account_id :
            criteria['account_id'] = account_id
            
        if category :
            criteria['category'] = category
        
        if mobile :
            criteria['mobile'] = mobile
            
        if email :        
            criteria['email'] = email
        
        if resend_code:
            criteria['resend_code'] = resend_code
        
        if criteria :
            table_cols = ['id','email', 'account_id', 'code', 'mobile', 'category', 'date_expiry', 'send_status', 'resend_code']
            
            try:
                result = self.dbconn.execute_select(
                            table_name='verification', 
                            conditions=criteria, 
                            operator='AND',
                            table_cols=table_cols, 
                            fetchall=False)
            
            except Exception, e :
                raise VerificationError('unable to retrieve verification: %s' % e)
                
            
            if result :
                
                verification_object = Verification()
                
                verification_object.verification_id = result['id']
                verification_object.email = result['email']
                verification_object.account_id = result['account_id']
                verification_object.code = result['code']
                verification_object.resend_code = result['resend_code']
                
                verification_object.mobile = result['mobile']
                verification_object.verification_category = result['category']
                
                # magically retured as datetime object
                verification_object.date_expiry =  result['date_expiry']
                
        return verification_object


    def get_change_email_verification_by_code(self, code, resend_code ):
        '''
        wrapper for get_verification() passes the code and category
        as parameter
        '''
        verifi = self.get_verification( code=code, resend_code=resend_code, category=self.valid_categories['change_email'] )
        
        return verifi
        
        
         

    def get_existing_change_email_verification( self, account_id, email ):
        '''
        wrapper for get change email verification
        this was created so that the model does not need to know the category name 'CHANGEEMAIL'
        '''
        
        category = self.valid_categories['change_email']
        verification = self.get_verification( email=email, category=category, account_id=account_id )
        return verification
        
        
    def get_forgot_password_verifi_by_code(self, code ):
        
        
        verification = self.get_verification( code=code, category=self.valid_categories['password'] )
        return verification



    def create_new_signup_verification(self, account_id, email, code , resend_code, expiration_delta=None):
        '''
        writes signup verification to verification table
        
        @param account_id: the account id assigned to the pending user
        @param email: the email used by the registering user
        @param code : String the unique string that will publicly identify the verification
        @param expiration_delta : python timedelta , denotes duration of validity of the verification
        
        
        @author: vincent agudelo
        
        
        '''
        verification_id = None
        
        new_verification_object = None
        params = {
                  'email' : email,
                  'account_id': account_id,
                  'code' : code,
                  'resend_code' : resend_code,
                  'category' : 'SIGNUP'
                  }

        if expiration_delta :
            params['date_expiry'] = (datetime.now() + expiration_delta).strftime('%Y-%m-%d %H:%M:%S')
        
        try :
        
            verification_id = self.__insert_to_database(params)
            
            
            new_verification_object = Verification()
            new_verification_object.verification_id = verification_id
            new_verification_object.email = email
            new_verification_object.verification_category = 'SIGNUP'
            new_verification_object.account_id = account_id
            new_verification_object.code = code             
            new_verification_object.resend_code = resend_code             
            
            
            
        except Exception, e :
            
            raise VerificationError('could not create verification record: %s' % e)

        return new_verification_object
    
    
    def create_new_change_email_verification(self, account_object, new_email, code, expiration_delta, resend_code ):
        
        verification_object = None
        
        params = {
                  'email' : new_email,
                  'account_id': account_object.account_id,
                  'code' : code,
                  'resend_code' : resend_code,
                  'category' : self.valid_categories['change_email'],
                  'date_expiry' : (datetime.now() + expiration_delta).strftime('%Y-%m-%d %H:%M:%S')
                  }
        
        try :
        
            verification_id = self.__insert_to_database(params)
            
            
            if verification_id :
                
                verification_object = Verification()
                
                
                verification_object.verification_id = verification_id
                verification_object.email = params['email']
                verification_object.verification_category = params['category']
                verification_object.account_id = params['account_id']
                verification_object.code = params['code'] 
                verification_object.resend_code = params['resend_code'] 
                
                
            
            
        except Exception, e :
            
            raise VerificationError('could not create verification record: %s' % e)
                
        
        return verification_object
        
    
    def create_new_forgot_pasword_verification(self, account_object, code, expiration_delta, resend_code  ):
        
        verification_object = None

        params = {
                  'email' : account_object.email,
                  'account_id': account_object.account_id,
                  'code' : code,
                  'resend_code' : resend_code,
                  'category' : self.valid_categories['password'],
                  'date_expiry' : (datetime.now() + expiration_delta).strftime('%Y-%m-%d %H:%M:%S')
                  }

        try :
            
            verification_id = self.__insert_to_database(params)

            if verification_id :
                
                verification_object = Verification()
                
                verification_object.verification_id = verification_id
                verification_object.email = params['email']
                verification_object.verification_category = params['category']
                verification_object.account_id = params['account_id']
                verification_object.code = params['code']
                verification_object.resend_code = params['resend_code']
            
        except Exception, e :
            raise VerificationError('could not create verification record: %s' % e)
            

        return verification_object


        
    def __insert_to_database(self, params ):
        '''
        inserts into database table the new record
            all new records have
          date created
          send status = PENDING
        '''
        
        params['date_created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
        return self.dbconn.execute_insert( table_name='verification', params=params)

        
    def get_mobile_code(self, account_id, testmin):
        if testmin:
            testmin = '639%s' %str(testmin[-9:])
        
        criteria = { 
            'account_id': account_id, 
            'mobile': testmin, 
            'category': 'MOBILE'
        }
        table_cols = [
            'code',
            'date_expiry',
            'id'
        ]
        try:
            return self.dbconn.execute_select(
                table_name='verification', 
                conditions=criteria, 
                operator='AND', table_cols=table_cols, 
                fetchall=False)
        
        except Exception, e:
            print e
            raise e
        return False
                
    
    def save_mobile_code(self, account_id, code, mobile):
        params = {
            'account_id': account_id,
            'code': code,
            'category': 'MOBILE',
            'mobile': mobile,
            'date_expiry': datetime.now() + timedelta(hours=EXPIRATION_PINCODE)
        }
         
        try:
            return self.dbconn.execute_insert(
                table_name='verification', params=params)
        
        except Exception, e:
            if 'Duplicate entry' in str(e):
                if "for key 'suffix'" in str(e) :
                    raise DuplicateVerificationCodeException(suffix=suffix)
            else:
                raise e
                
    def update_mobile_code(self, account_id, code=None, mobile=None, ver_id=None):
        criteria = {
            'account_id': account_id, 
            'category': 'MOBILE'
        }
        
        if mobile:
            criteria['mobile'] = mobile
            
        params = {
            'date_expiry': datetime.now() + timedelta(hours=EXPIRATION_PINCODE)
        }
        
        if code:
            params['code'] = code
        if ver_id: 
            params['id'] = ver_id
            
        try:
            if len(params) == 1:
                return self.dbconn.execute_update(
                    table_name='verification', params=params,
                    conditions=criteria)
            elif len(params) > 1:
                return self.dbconn.execute_update(
                    table_name='verification', params=params,
                    operator='AND', conditions=criteria)
                    
        except Exception, e:
            if 'Duplicate entry' in str(e):
                if "for key 'suffix'" in str(e) :
                    raise DuplicateVerificationCodeException(suffix=suffix)
            else:
                raise e        
                
    def delete_mobile_code(self, account_id, testmin):
        if testmin:
            testmin = '639%s' %str(testmin[-9:])
            
        criteria = {
            'account_id': account_id, 
            'category': 'MOBILE',
            'mobile': testmin
        }        
        try:
            return self.dbconn.execute_delete(
                table_name='verification', 
                operator='AND', conditions=criteria)
        except Exception, e:
            print e
            
            
    def get_min(self, account_id, verification_id):
        criteria = {
            'account_id': account_id,
            'id': verification_id
        }
        table_cols = ['mobile']
        try:
            return self.dbconn.execute_select(
                table_name='verification', 
                conditions=criteria, 
                operator='AND',
                table_cols=table_cols, 
                fetchall=False)
     
        except Exception, e:
            raise e
    
    # --- REDIS FUNCTIONS ---
    
    def get_code_request_count(self, account_id, testmin):    
        if testmin:
            testmin = '639%s' %str(testmin[-9:])
        
        try:
            return self.redisconn.get(
                KEY_CODE_REQUEST_CTR % (account_id,
                testmin))
        except Exception, e:
            print e
            raise e
        return False
                
    def incr_code_request_count(self, account_id, testmin): 
        if testmin:
            testmin = '639%s' %str(testmin[-9:])  
            
        try:
            count = self.redisconn.incr(
                KEY_CODE_REQUEST_CTR % (account_id, testmin))
            if str(count) == '1':
                self.redisconn.expire(
                KEY_CODE_REQUEST_CTR % (account_id, testmin),
                KEY_CODE_REQUEST_EXPIRATION)
            
            return count
        except Exception, e:
            print e
            raise e
        return False       
  
    def get_code_unverified_requests(self, account_id):
        try:
            return self.redisconn.get(
                KEY_CODE_UNVERIFIED_REQUEST_CTR % account_id)
        except Exception, e:
            print e
            raise e
        return False
    
    def set_code_unverified_requests(self, account_id, unverified_min_list):
        try:
            return self.redisconn.setex(
                KEY_CODE_UNVERIFIED_REQUEST_CTR % account_id, 
                dumps(unverified_min_list), KEY_CODE_REQUEST_EXPIRATION)
        except Exception, e:
            print e
            raise e
        return False
    
    
    def get_code_tries_count(self, account_id, testmin):     
        try:       
            if testmin:
                testmin = '639%s' %str(testmin[-9:])
            
            return self.redisconn.get(
            KEY_CODE_TRIES_CTR % (account_id, testmin))
        except Exception, e:
            print e
            raise e
        return False
                    
    def incr_code_tries(self, account_id, testmin):
        try:
        
            # prevents forced injection
            account_id = int(account_id)
                    
            if testmin:
                testmin = '639%s' %str(testmin[-9:])
                
            testmin = int(testmin)
            
            tries = self.redisconn.incr(
                KEY_CODE_TRIES_CTR % (str(account_id), str(testmin)))
            if str(tries) == '1':
                self.redisconn.expire(
                KEY_CODE_TRIES_CTR % (str(account_id), str(testmin)),
                KEY_CODE_REQUEST_EXPIRATION)
            return tries
        except Exception, e:
            print e
            raise e
        return False

    def set_message_sent_to_pending(self, mobile, message_id):
        try:
            KEY = KEY_MESSAGE_SENT_FLAG % (
                str(mobile), str(message_id))
            return self.redisconn.setex(KEY,
                'PENDING', KEY_MESSAGE_SENT_FLAG_EXPIRATION)
        
        except Exception, e:
            print e
            raise e
            
    def set_message_sent_to_success(self, mobile, message_id):
        try:
            KEY = KEY_MESSAGE_SENT_FLAG % (
                str(mobile), str(message_id))
            if not self.redisconn.exists(KEY):
                # the sending of test MT already expired
                return None
            return self.redisconn.setex(KEY,
                'SUCCESS', KEY_MESSAGE_SENT_FLAG_EXPIRATION)
        
        except Exception, e:
            print e
            raise e
        
    def get_message_sent_status(self, mobile, message_id):
        try:
            KEY = KEY_MESSAGE_SENT_FLAG % (
                str(mobile), str(message_id))
            return self.redisconn.get(KEY)
        
        except Exception,e :
            print e
            raise e
    
