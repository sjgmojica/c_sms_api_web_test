'''

model for sms user account

@author: vincent agudelo
@author: jhesed

'''

from datetime import datetime
from utils.code_generation import create_sha256_signature
import utils.add_sms_credits as credit_tool 

class Account( object ):
    
    input_error = False
    dao = None
    cache_dao = None
    
    max_login_attempts_per_day = 5
    
    #--- model constants
    PACKAGE_FREE = 100
    PACKAGE_PAID = 101
    PACKAGE_INACTIVE = 102
    PACKAGE_UNPAID = 103
    
    
    package_type = None
    
    
    cart_count = 0
    balance = ''
    
    secret_key=None
    client_id=None


    balance_notif_enabled = True
    balance_notif_threshold = 50

    # generic name
    name = ''
    
  
    def __init__(self):
        self.password = None
        self.company_name = None
        self.address = None
        self.account_id = None
        self.email = None  
        
        self._status = None
        self._first_name = None
        self._last_name = None
        self._company_name = None
        self._address = None

        self._password = None

        self._change_mobile_ctr = None
        
        # not to be set in the model
        self._is_pending = None
        self._is_active = None
        self._is_inactive = None
        self.balance_formatted = ''
        self.billing_email = ''
        
        self.test_mo_reply = None
        
    @staticmethod
    def get_user_by_login( email, password ):
        
        
        account = None
        
        failed_attempts = 0
        
        account = Account.get_raw_info( email=email )
        
        if not account :
            # user does not exist
            raise AccountNotExist
        
        if account.is_pending() :
            raise AccountExistInvalidPassword
        
        if  account.is_active() and  account._password != password :

            # step 1 
            # increment invalid password tries
            failed_attempts = Account.increment_failed_login_attempt( account_id=account.account_id )

            if failed_attempts > Account.max_login_attempts_per_day :
            
                raise FailedLoginAttemptsExceeded()
            
            # step 2 raise exception
            raise AccountExistInvalidPassword
        

        # if code reaches here, then login must be good
        # delete failed attempt counter
        Account.cache_dao.delete_failed_attempt_ctr( account_id=account.account_id )
        
        
        return account


    @staticmethod
    def increment_failed_login_attempt( account_id ):
        '''
        increments failed login attempts of a
        '''
        failed_attempts = Account.cache_dao.increment_failed_attempted_login( account_id=account_id )
        
        return failed_attempts



    def update_name(self, name=None):
        
        #simple sanitize
        
        name = name.replace('\\','')
        
        # prevent blank
        if name :
            Account.dao.update_name( account_id=self.account_id, name=name )

    
    @property
    def first_name(self):
        
        return self._first_name
    
    @first_name.setter
    def first_name(self, value):
        '''
        make sure that first name rules are applied
        
        should only be 31 characters long
        
        '''
        if value and len(value) > 32 :
            self.first_name_error = 'first name is too long'
            self.input_error = True
            return
        
        
        self._first_name = value
        
    @property
    def last_name(self):
        
        return self._last_name
    
    @last_name.setter
    def last_name(self, value):
        '''
        make sure that first name rules are applied
        '''
        
        self._last_name = value

    @property
    def change_mobile_ctr(self):
        return self._change_mobile_ctr    
    
    @property
    def change_mobile_ctr(self):
        return self._change_mobile_ctr    
    
    @property
    def company_name(self):
        return self._company_name

    @company_name.setter
    def company_name(self, value):
        
        self._company_name = value
        
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        
        self._address = value

    @property
    def status(self):
        
        return self._status
    
    
    @status.setter
    def status(self, value):
        
        self._status = value
    
    def is_active(self):
        '''
        determine if account is active
        '''

        if self._is_active is None :
            return False
        else :
            return self._is_active        
        
        
    def set_to_paid_package(self):
        
        result = Account.dao.set_to_paid_package( account_id=self.account_id )
        
        return result

        
    def is_pending(self):
        '''
        determine if account is pending
        '''
        
        if self._is_pending is None :
            return False
        else :
            return self._is_pending
        

    def create_pending_account(self):
        '''
        creates a pending account in database
        used ONLY for registration
        @return: Boolean. if the account has been created in database
        '''
        
        return Account.dao.create_pending_user( self )

        
    def save(self):
        '''
        saves user details to respective storages
        '''
        if self.input_error :

            return False
        
        else:
            Account.dao.save( self )
            return True
  
  
    @staticmethod
    def set_active( account_id ):
        '''
        shortcut for set_status( account_id, 'ACTIVE' )
        
        @return: Boolean if the status was set
        '''
        
        success = Account.set_status( account_id, 'ACTIVE' )
    
    
        return success
    
  
    @staticmethod
    def set_status( account_id, status ):
        '''
        sets the account status of a user
        
        valid account status
        'PENDING','ACTIVE','INACTIVE'
        '''
        
        valid_status = ['PENDING','ACTIVE','INACTIVE']
        
        success = False 
        
        if status in valid_status :
            
            success = Account.dao.set_account_status( account_id=account_id, status=status )
        
        
        return success 
  
  
    @staticmethod
    def get( account_id=None, user_id=None, email = None, suffix=None, **kwargs):
        '''
        account_id should be used to be more consistent
        
        '''
        account = Account.dao.get( account_id=account_id, email=email, suffix=suffix, **kwargs)
        
        if account:
            account.free_credits = Account.cache_dao.get_free_credits( suffix=account.suffix )
            
            # load balance (if paid account)
            if account.package_type == Account.PACKAGE_PAID :
                try:
                    account.balance = credit_tool.get_balance( account.suffix )
                    #locale.setlocale(locale.LC_ALL, 'en_US')
                    if not account.balance:
                        account.balance=0
                    #account.balance_formatted = 'P%s' % locale.format('%0.2f', float(account.balance), grouping=True)
                    account.balance_formatted =  'P%s' % (  format( account.balance, ',.2f' )   )
                except Exception, e:
                    print 'error get balance: %s' % e
                 
        
        return account

    def refresh_credit_balance(self):
        '''
        retrieves credits and determines if balance notif flags would be reset
        '''
        
        current_credit_balance =self.balance
        self.balance = credit_tool.get_balance( self.suffix )

        if current_credit_balance == 0:
            # remove zero balance flag
            self.reset_zero_balance_notif_sent()
        
        if self.balance > self.balance_notif_threshold :
            # reset sent flags
            self.reset_balance_threshold_notif_sent( )
         


    @staticmethod
    def get_raw_info( id=None, email=None ):
        '''
        !!! WARNING !!!
        do not use this function for standard features
        
        to be used to get raw info on a user (complete / incomplete) 
        
        '''
        
        #account_object = Account()
        #account_object.email = email
        #account_object.account_id = id
        
        account_object = Account.dao.get_raw_info( id=id, email=email )
        
        
        return account_object
    
    def change_email(self, new_email ):
        '''
        change the email of user
        '''
        
        if self.email == new_email :
            raise SameEmailError()
        
        
        success = Account.dao.change_email( account_id=self.account_id, new_email=new_email )
        
        return success
    
    def change_billing_email(self, billing_email ):
        '''
        saves billing email
        
        @raise AccountSaveException: when error occurs in trying to save in database 
        '''
        
        try:
            success = Account.dao.update_billing_email( account_id=self.account_id, billing_email=billing_email )
        except Exception, e:
            raise AccountSaveException( 'unable to save billing email: %s' % e )
    
    def delete_if_pending(self):
        '''
        wrapper to delete if pending
        '''
        
        if self.is_pending():
            Account.dao.delete( account_id=self.account_id )


    @staticmethod
    def get_mo_reply(account_id):
        return Account.dao.get_mo_reply(account_id)
                        
    @staticmethod
    def save_testmin(account_id, testmin):      
        return Account.dao.save_testmin(account_id, testmin)
        
    @staticmethod
    def update(account_id, package=None, 
        test_mo_reply=None, **kwargs):
        return Account.dao.update(
            account_id, package, test_mo_reply, **kwargs)
        
    @staticmethod
    def update_suffix(account_id, suffix):
        return Account.dao.update_suffix(
            account_id, suffix)
            
    @staticmethod
    def was_testmin_prev_verified(account_id, testmin):
        return Account.dao.was_testmin_prev_verified(account_id, testmin)



    def check_same_old_password( self,password ):
        '''
        check if account does not exist / pending
        
        @raise AccountNotExist: if account does not exist
        '''
        
        if self.is_active() is True :
            if self._password != password :
                return False
            else :
                return True

        else:
             AccountNotExist('does not exist')
             
    def save_new_password(self, new_password):
        '''
        saves password to datase
        DO NOT USE WITHOUT BUSINESS RULES
        '''
        
        result = Account.dao.save_new_password( account_id=self.account_id, new_password=new_password )
        
        return result

    def generate_secret_key(self):
        '''
        sets a new secret key
        
        '''
        new_secret_key = None
        
        # only happens when you have a suffix
        if self.suffix :
        
            new_secret_key = create_sha256_signature(suffix=self.suffix, email=self.email)

            # save to database
            
            Account.dao.update_secret_key( account_id=self.account_id, secret_key=new_secret_key)

            # save in cache
            Account.cache_dao.update_secret_key( suffix=self.suffix, secret_key=new_secret_key )
        
        return new_secret_key
    
    def set_balance_threshold_notif_sent(self):
        Account.cache_dao.set_balance_threshold_notif_sent( suffix=self.suffix )
        
    def reset_balance_threshold_notif_sent(self):
        Account.cache_dao.set_balance_threshold_notif_sent( suffix=self.suffix, sent=False )

        
    def get_balance_threshold_notif_sent(self):
        '''
        fetches data from cache
        the data refers to if a notification was previously sent
        '''
        
        sent = Account.cache_dao.get_balance_threshold_notif_sent( suffix=self.suffix )
        return sent
        

    def get_zero_balance_notif_sent(self):
        sent = Account.cache_dao.get_zero_balance_notif_sent( suffix=self.suffix )
        return sent 
    

    def set_zero_balance_notif_sent(self):
        Account.cache_dao.set_zero_balance_notif_sent( suffix=self.suffix )
        
    
    def reset_zero_balance_notif_sent(self):
        '''
        resets the flag that says notification was sent
        
        '''
        
        
        Account.cache_dao.set_zero_balance_notif_sent( suffix=self.suffix, sent=False )
        
    

    def enable_balance_notification(self ):
        '''
        sets the balance notification and balance threshold
        '''
        
        Account.dao.update_balance_notif_settings(account_id=self.account_id, enabled=True, threshold=self.balance_notif_threshold)
        


    def disable_balance_notification(self):
        '''
        disables the balance notification
        '''
        Account.dao.update_balance_notif_settings(account_id=self.account_id, enabled=False, threshold=self.balance_notif_threshold)
        
    def set_balance_threshold(self):
        
        Account.dao.update_balance_notif_settings(account_id=self.account_id, enabled=self.balance_notif_enabled, threshold=self.balance_notif_threshold)


class DuplicateEmailException(Exception):
    
    email=None
    
    def __init__(self, email):
        self.email = email
    
    def __str__(self):
        
        return 'the email %s already exists in database' % self.email

class AccountSaveException( Exception ):
    pass

class DuplicateSuffixException(Exception):
    '''
        Custom exception triggered
        when inserting duplicate
        suffixes in table
    ''' 
    
    error_spiel = 'Suffix %s already already taken'
   
    def __init__(self, suffix):
        self.suffix = str(suffix)
    
    def __str__(self):
        return self.error_spiel % self.suffix

class AccountLoadException( Exception ):
    pass

class ActiveAccountAlreadyExisting( Exception ):
    pass

class PendingAccountAlreadyExisting( Exception ):
    verification_object = None
    
    def __init__(self, verification_object=None ):
        
        self.verification_object = verification_object

    def __str__(self):
        if self.verification_object:
            return 'has existing verification. account_id=%s' % self.verification_object.account_id
        else:
            return 'has existing verification'


class SameEmailError( Exception ):
    '''
    raised when user input email is the same as current email
    '''
    pass

class AccountNotExist( Exception ):
    pass

class AccountExistInvalidPassword( Exception ):
    pass
class FailedLoginAttemptsExceeded( Exception ):
    pass
class SameToOldPassword( Exception ):
    pass


