'''
this file contains data manipulation to and from mysql

@author: vincent agudelo
@author: jhesed tacadena
'''

from models.account import Account, DuplicateEmailException, AccountSaveException

from datetime import datetime

class AccountMySQLDAO( object ):
    
    active_user_status = 'ACTIVE'
    def __init__(self, sql_util=None):
        self.mysql_util = sql_util


    def get_user_by_login(self, email, password):
        
        
        criteria = {
                    'email' : email,
                    'password' : password,
                    'status' : self.active_user_status
                    }
        
        table_cols = ['id', 'email', 'first_name', 'last_name']
        
        
        record = self.mysql_util.execute_select(
            table_name='accounts', 
            conditions=criteria, 
            operator='AND', table_cols=table_cols, 
            fetchall=False)
        
        valid_user = None
        
        if record :
            
            valid_user = Account()
            
            valid_user.account_id = record['id']
            valid_user.email = record['email']
            valid_user.first_name = record['first_name']
            valid_user.last_name = record['last_name']
            valid_user._is_active = True
            
        
        return valid_user


    
    def set_to_paid_package(self, account_id ):
        '''
        sets the account status of a user to PAID
        
        '''
        result = self.__set_package(account_id=account_id, package='PAID')
        return result
    
    
    def __set_package(self, account_id, package ):
        '''
        sets the package of value of an account
        
        valid packages 'FREE','PAID','INACTIVE'
        
        '''
        
        result = None
        
        params = {'package' : package }
        conditions = { 'id': account_id }
        
        result = self.__update_record(params=params, conditions=conditions)
        if result :
            return True
        else :
            return False
        
        return result
        
        
    

    def create_pending_user(self, account_object):
        import sys, traceback 
        
        fields = {
                  'email' : account_object.email,
                  'password':account_object.password,
                  'date_created' :datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                  }
        
        #probable optional values
        if account_object.first_name is not None :
            fields['first_name'] = account_object.first_name 
        
        if account_object.last_name is not None :
            fields['last_name'] = account_object.last_name
            
        if account_object.company_name is not None :
            fields['company'] = account_object.company_name
            
        if account_object.address is not None :
            fields['address'] = account_object.address
        
        try:
            # select muna
            criteria = { 'email':account_object.email }
            result = self.mysql_util.execute_select( table_name='accounts',
						    conditions=criteria,
						    operator='AND', table_cols=fields,
						    fetchall=False )
            print 'SELECT' , result
            if result :
                raise Exception('Duplicate entry \'%s\' for key \'email\''% account_object.email )


            result = self.mysql_util.execute_insert('accounts', fields)
            if result :
                print 'result true' 
                account_object.account_id = result
            
                # should deprecate this flag
                account_object.status = 'PENDING'
                
                account_object._is_pending = True
                
                return True
            
        except Exception, e :
            #print repr(traceback.format_exception(exc_type, exc_value,
            #                             exc_traceback))

            if 'Duplicate entry' in str(e):
                print 'PAASOK'
                if "for key 'email'" in str(e) :
                    raise DuplicateEmailException( email=account_object.email )
            else:
                raise AccountSaveException('unable to create pending account: %s' % e)

            
        return False
        

    def update_balance_notif_settings(self, account_id, enabled, threshold):
        '''
        @param enabled: boolean. set to enable/disable billing info
        @param threshold: integer. value to set the threshold balance 
        
        this is a generic function to update balance notification settings
        
        '''
        conditions = { 'id':account_id }
        params = {  }
        
        if enabled :
            params['with_balance_notif'] = 1
        else:
            params['with_balance_notif'] = 0
        
        
        params['balance_threshold'] = threshold
        
        self.__update_record( params, conditions )
    
    def save( self, account_object ):
        '''
        saves the account in database
        '''
        print 'DAO EXECUTE', self.mysql_util
        query_str = 'SELECT * FROM account'
        
        data = self.mysql_util.run_query('select', query_str, dictionary=True)
        
        
    def save_new_password(self, account_id, new_password ):
        '''
        saves the passwords field with new password
        
        '''
        params = {'password':new_password}
        conditions = {'id':account_id}
        result = self.__update_record( params, conditions )
        
        return result
        
    def update_secret_key(self, account_id, secret_key):
        '''
        updates the secret key in database
        secret key should ONLY be a string 64 characters long,
        composed of hexadecimal characters
        
        '''
        
        params = {'secret_key':secret_key}
        conditions = {'id':account_id}
        print 'saving secret key'
        result = self.__update_record( params, conditions )
        
        return result
        
        
        


    def get(self, account_id=None, email=None , suffix=None, **kwargs):
        
        criteria = {}
        
        
        # maybe we can also get account object via email address
        if account_id :
            criteria['id'] = account_id
            
        if email :
            criteria['email'] = email
        
        if suffix :
            criteria['suffix'] = suffix
        
        
            
        if not criteria :
            return None
        
        table_cols = [
            'id', 'first_name', 'last_name','email', 'suffix', 'test_min', 'change_mobile_ctr', 
            'test_mo_reply', 'status', 'address', 'company', 'package', 'password', 
            'secret_key', 'client_id', 'name', 'billing_email', 'with_balance_notif', 'balance_threshold'
        ]
        
        
        account_object = None
        
        try :
            
            result = self.mysql_util.execute_select(
            table_name='accounts', 
            conditions=criteria, 
            operator='AND', table_cols=table_cols, 
            fetchall=False)
            
            if result :
                account_object = Account() 
                account_object.account_id = result['id'] 
                account_object.first_name = result['first_name']
                account_object.last_name = result['last_name']
                account_object.test_min = result['test_min']
                account_object._change_mobile_ctr = result['change_mobile_ctr']
                account_object.test_mo_reply = result['test_mo_reply']
                account_object.suffix = result['suffix']
                account_object.address = result['address']
                account_object.company = result['company']
                account_object._password = result['password']

                account_object.email = result['email']
                account_object.package = result['package']
                account_object.secret_key = result['secret_key']
                account_object.client_id = result['client_id']
                account_object.name = result['name']
                account_object.billing_email = result['billing_email']
                
                account_object.balance_notif_enabled = True if result['with_balance_notif'] else False
                account_object.balance_notif_threshold = result['balance_threshold']
                

                if result['package'] == 'FREE' :
                    account_object.package_type = Account.PACKAGE_FREE
                elif result['package'] == 'PAID' :
                    account_object.package_type = Account.PACKAGE_PAID
                elif result['package'] == 'INACTIVE' :
                    account_object.package_type = Account.PACKAGE_INACTIVE
                elif result['package'] == 'UNPAID' :
                    account_object.package_type = Account.PACKAGE_UNPAID
                
                
                
                # set user status
                if result['status'] == 'PENDING' :
                    account_object._is_pending = True
                elif result['status'] == 'ACTIVE' :
                    account_object._is_active = True
                elif result['status'] == 'INACTIVE' :
                    account_object._is_inactive = True
                
        except Exception, e :
            # @todo raise error
            pass
        
        return account_object

    def get_raw_info(self, id=None, email=None ):
        
        conditions={}
        
        if id :
            conditions['id'] = id

        if email :
            conditions['email'] = email
        
        if not conditions :
            return None 
        
        table_cols = [ 'id', 'suffix', 'package', 'address','company','first_name','last_name', 'email', 'suffix', 'test_min','change_mobile_ctr',
                      'date_created', 'date_updated', 'change_mobile_ctr', 'test_min', 'test_mo_reply', 'status', 'password']
        
        try :
            
            account_object = None
            
            result = self.mysql_util.execute_select(
                table_name='accounts', 
                conditions=conditions, 
                operator='AND', table_cols=table_cols, 
                fetchall=False)
                
            if result :
                
                #map the values to 
                account_object = Account() 
                account_object.account_id = result['id'] 
                account_object.first_name = result['first_name']
                account_object.last_name = result['last_name']
                account_object._password = result['password']
                
                # should deprecate
                account_object.status = result['status']
            
                # set user status
                if result['status'] == 'PENDING' :
                    account_object._is_pending = True
                elif result['status'] == 'ACTIVE' :
                    account_object._is_active = True
                elif result['status'] == 'INACTIVE' :
                    account_object._is_inactive = True

            
        except Exception, e:
            
            raise AccountLoadException('unable to load account id=%s email=%s ; %s' % (id,email,e) )
        
        else :
        
            return account_object


    def save_testmin(self, account_id, testmin):  
        testmin = '639%s' %str(testmin[-9:])
        query_str = "UPDATE accounts set test_min='%s',\
            change_mobile_ctr=change_mobile_ctr+1 WHERE id='%s'" % (
            testmin, account_id)
        try:
            return self.mysql_util.run_query('update', 
                query_str, dictionary=True)
        except Exception, e:
            print e
            raise e
        return False
                        
    def update_name(self, account_id, name ):
        '''
        updates the name field in user account record
        '''
        
        params = {'name': name }
        conditions = {'id' : account_id }
        
        self.__update_record(  params, conditions )
        
    def update_billing_email(self, account_id, billing_email ):
        '''
        updates the billing email field in user account record
        '''
        params = {'billing_email': billing_email }
        conditions = {'id' : account_id }
        self.__update_record(  params, conditions )        
    
    def update(self, account_id, package=None, test_mo_reply=None, **kwargs):
        '''
            Updates table accounts row based
            on the parameters passed
        '''
        criteria = {
            'id': account_id
        }
        params = {}
        if package:
            params['package'] = package
        if test_mo_reply:
            params['test_mo_reply'] = test_mo_reply
        if 'firstname' in kwargs:
            params['first_name'] = kwargs['firstname']
        if 'lastname' in kwargs:
            params['last_name'] = kwargs['lastname']
        if 'company' in kwargs:
            params['company'] = kwargs['company']
        if 'address' in kwargs:
            params['address'] = kwargs['address']
        if 'client_id' in kwargs:
            params['client_id'] = kwargs['client_id']
        if 'secret_key' in kwargs:
            params['secret_key'] = kwargs['secret_key']
            
        try:
            if len(params) == 1:
                return self.mysql_util.execute_update(
                    table_name='accounts', params=params, 
                    conditions=criteria)
            else:        
                return self.mysql_util.execute_update(
                    table_name='accounts', params=params, 
                    conditions=criteria, operator='AND')
        
        except Exception, e:
            raise e
    
    def __update_record( self, params, conditions ):
        '''
        executes update query based on give raw params and conditions
        
        '''
        
        result = False
        
        try:
            result = self.mysql_util.execute_update(
                table_name='accounts', params=params, 
                conditions=conditions, operator='AND')
        
        except Exception, e :
            
            # try to parse errors
            if 'Duplicate entry' in str(e):
                if "for key 'email'" in str(e) :
                    raise DuplicateEmailException( email=account_object.email )
            else:
                raise AccountSaveException('unable to update user: %s' % e )        
            
        if result :
            return True
        else :
            return False
        


    def set_account_status(self, account_id, status ):
        
        criteria = { 
                  'id' : account_id
                   }
        params = {'status':status}
        
        
        success_return = False
        
        try :
            
            success = self.mysql_util.execute_update(
            table_name='accounts', params=params, 
            conditions=criteria, operator='AND')
            
            
            if success == 1 :
                success_return = True

        except Exception,e:
            raise AccountSaveException('unable to set account status %s to id:%s : %s' % (status, account_id, e) )
            
        return success_return

    def update_suffix(self, account_id, suffix):
        criteria = {
            'id': account_id
        }
        params = {
            'suffix': suffix
        }
        try:
            self.mysql_util.execute_update(
                table_name='accounts', params=params, 
                conditions=criteria)
            
        except Exception, e:
            if 'Duplicate entry' in str(e):
                if "for key 'suffix'" in str(e) :
                    raise DuplicateSuffixException(suffix=suffix)
            else:
                raise e
                
    def was_testmin_prev_verified(self, account_id, testmin):
        if testmin:
            testmin = '639%s' %str(testmin[-9:])
            
        criteria = {
            'id': account_id,
            'test_min': testmin
        }
        table_cols = ['id', 'change_mobile_ctr']
        try:
            return self.mysql_util.execute_select(
                table_name='accounts', 
                conditions=criteria, 
                operator='AND', table_cols=table_cols, 
                fetchall=False)
        except Exception, e:
            print e
            raise e
        return False

    
    def change_email(self, account_id, new_email ):
        '''
        updates the email field of mysql
        
        this SHOULD RAISE a duplicate error exception if existing email exists
        
        @author: vincent agudelo
        '''
        
        success = False
        
        params = {
                  'email' : new_email
                  }
        
        conditions = {
                      'id' : account_id
                      }
        
        success = self.__update_record( params, conditions )
        
        return success        
        
        
    def delete(self, account_id ):
        '''
        deletes user from accounts table
        '''
        
        conditions = { 'id': account_id }        
        
        result = None
        
        try:

            result = self.mysql_util.execute_delete( 'accounts', conditions )
            
            
        except Exception, e:
            raise Exception( e )
        
        return result
