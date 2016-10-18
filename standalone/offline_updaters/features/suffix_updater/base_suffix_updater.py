'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
        - contains functions usable
        by the more specific classes
'''

import datetime
import gredis.client
from utils.configuration import Configuration
from utils.sql_tools import SQLUtils
import features.logging as sms_api_logger

class BaseSuffixUpdater(object):
    
    dbconn = None
    redisconn = None    
        
    query_del_from_claimed_suffix = """delete from claimed_suffixes where account_id='%s'"""
    query_del_from_accounts = """update accounts set suffix=NULL, package='INACTIVE' where id='%s'"""
    key_cached_suffix = 'SMSAPI_%s'            
    key_cached_suffix_credits = 'SMSAPI_%s_CREDITS'            
    key_zero_credit_date = 'ZERO_CREDIT_DATE'
    
    
    def init(self):
            '''
                @description:
                    intializes:
                        - configurations
                        - db connections
            '''
            Configuration.initialize()
            values = Configuration.values()            
            
            self.dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
                port=values['mysql-db']['sms_api_config']['port'],
                database=values['mysql-db']['sms_api_config']['db'],
                user=values['mysql-db']['sms_api_config']['user'],
                password=values['mysql-db']['sms_api_config']['password'])
            
            self.redisconn = gredis.client.Connection(address=
                str(values['redis_servers']['sms_api']['host']), 
                port=int(values['redis_servers']['sms_api']['port']))
            self.redisconn.connect()
            
            print '-------'
            print 'redis:'
            print 'port: %s' %values['redis_servers']['sms_api']['port']
            print 'host: %s' %values['redis_servers']['sms_api']['host']
            print '\n'
            print 'sql:'
            print 'port: %s' %values['mysql-db']['sms_api_config']['host']
            print 'host: %s' %values['mysql-db']['sms_api_config']['port']
            print 'db: %s' %values['mysql-db']['sms_api_config']['db']
            print 'user: %s' %values['mysql-db']['sms_api_config']['user']
            print 'password: %s' %values['mysql-db']['sms_api_config']['password']
            print '-------'
                
                
    def select_suffix(self, package='FREE', suffix='', extra_query=None, days='30'):
        '''
            @description:
                - returns a list of ids and suffixes based
                from the params passed
        '''
        
        if not extra_query:
            query = """select a.id, a.suffix, b.date_created from accounts as a,
                claimed_suffixes as b where a.status = 'ACTIVE' and a.package = '%s'
                and a.suffix = b.suffix and a.id = b.account_id and b.date_created + INTERVAL '%s' DAY 
                < now()"""  %(package, str(days))
        else:
            query = """select a.id, a.suffix, b.date_created from accounts as a,
                claimed_suffixes as b where a.status = 'ACTIVE' and a.package = '%s'
                and a.suffix = b.suffix and a.id = b.account_id and %s"""  %(package, extra_query)
            
        print '\n - select suffix QUERY: - \n'
        print ' '.join(query.split())
        
        try:
            return self.dbconn.run_query(query_type='select', query=query,
                fetchall=True)
        except Exception, e:
            print e
        return None
    
    def has_pending_purchase(self, account_id, status, date=None, 
        grace_period_in_days=30, zero_credit_date=None, suffix=None):
        '''
            @description:
                - returns true if user has pending purchase
                else false
            @param:
                - status: in ['PENDING', 'INACTIVE']
                - date: date the 
                - grace_period_in_days: defined grace period in days based 
                    on package type (i.e. FREE | PAID | UNPAID | INACTIVE),
                    based on use case
        '''

        if not zero_credit_date:
            date_with_grace_period = self.compute_date_with_grace_period(
                date, grace_period_in_days)
        else:
            date_with_grace_period = self.compute_date_with_grace_period(
                zero_credit_date, grace_period_in_days)
            
            print 'has_pending_purchase -- date with grace period -- %s' %str(date_with_grace_period)
                
        if zero_credit_date:
            query = """select id from checkout where account_id=%s 
                and status='%s' and date_created >= '%s' 
                and date_created <= '%s'
                and (date_created + INTERVAL 30 DAY) > now()
                and suffix='%s'""" %(
                account_id, status, zero_credit_date,
                date_with_grace_period, suffix) 
        
        else:        
            # query = """select id from checkout where account_id=%s 
                # and status='%s' and date_created >= '%s' 
                # and date_created <= '%s'
                # and (date_created + INTERVAL 30 DAY) <= now()""" %(
                # account_id, status, date,
                # date_with_grace_period) 
                
            query = """select id from checkout where account_id=%s 
                and status='%s' and suffix='%s' and (date_created + INTERVAL 30 DAY) >= now()""" %(
                account_id, status, suffix) 
        
        print '\n - checkout QUERY -\n'
        print query
        
        try:

            has_pending_purchase = self.dbconn.run_query(query_type='select', 
                query=query, fetchall=True)
                
            print 'has_pending_purchase CHECKOUT ID: %s ' %has_pending_purchase
            
            return has_pending_purchase
        except Exception, e:
            print e
        
    def delete_suffixes(self, suffixes_info, status, grace_period_in_days, zero_credit_date=None, category='PAID_TO_INACTIVE'):
        '''
            @description:
                - deletes expired suffixes
                - used for FREE
        '''         
            
        if not suffixes_info:
            return None
        
        print 'total suffixes being checked: %s ' %str(len(suffixes_info))
        
        if category == 'FREE_TO_INACTIVE':
            su_logger = sms_api_logger.StandAloneSuffixFreeToInactiveLogger() 
        
        elif category == 'PAID_TO_INACTIVE':
            su_logger = sms_api_logger.StandAloneSuffixPaidToInactiveLogger() 
        
        elif category == 'UNPAID_TO_INACTIVE':
            su_logger = sms_api_logger.StandAloneSuffixUnpaidToInactiveLogger() 
        
        for ao in suffixes_info:
                           
            # removes claimed suffix after expiration period
            # if the account has not purchased anything 
            # (status=PENDING in checkout table)
            # in the window period
            
            # has_pending_purchase
            if not self.has_pending_purchase(ao['id'],
                status, ao['date_created'],
                grace_period_in_days, zero_credit_date,
                ao['suffix']):                
                
                print 'account %s -- no pending purchase' % ao['id']
                
                try:
                    
                    # --- actual deletion of suffixes ---
                    
                    print '\n - stored redis hash : - \n'
                    print self.redisconn.hgetall(self.key_cached_suffix % ao['suffix'])
                    print '---here---'
                
                    # delete suffix in claimed suffix table
                
                    print '\n - delete from claimed suffix QUERY: - \n'
                    print self.query_del_from_claimed_suffix % ao['id']
                    
                    su_logger.info('deleting row from claimed suffixes table', 
                        {'account_id': ao['id'], 'suffix': ao['suffix']})
                    
                    self.dbconn.run_query(query_type='delete', 
                        query=(self.query_del_from_claimed_suffix % ao['id']))                
                        
                    # delete suffix in accounts table
                    
                    print '\n - suffix to NULL in account table QUERY: - \n'
                    print self.query_del_from_accounts % ao['id']
                
                    su_logger.info('updating account table to suffix = NULL ', 
                        {'account_id': ao['id'], 'suffix': ao['suffix']})
                        
                    self.dbconn.run_query(query_type='update', 
                        query=(self.query_del_from_accounts % ao['id']))
                    
                    print '\n - redis del query: - \n'
                    print 'del %s' % self.key_cached_suffix % ao['suffix']
                    
                    su_logger.info('deleting in redis', 
                        {'account_id': ao['id'], 'suffix': ao['suffix']})
                        
                    # delete redis key for expired suffix
                    self.redisconn.delete(self.key_cached_suffix % ao['suffix'])
                
                except Exception, e:
                    import traceback
                    print traceback.format_exc()                    
                    su_logger.error('error when deleting suffix', 
                        {'error': str(e)})
                    print e
    
    def delete_expired_suffixes_with_zero_credits(self, suffixes_info,
            status, grace_period_in_days=90):
        
        if not suffixes_info:
            return None
        
        for si in suffixes_info:
        
            key_suffix_credits = self.key_cached_suffix_credits % si['suffix']
            key_suffix = self.key_cached_suffix % si['suffix']
                                    
            # checks if key_cached_suffix_credits exist.
            # if yes, key_zero_credit_date value should not 
            # exist in key_cached_suffix
            # else, retrieve key_zero_credit_date value
            
            try:
                
                print 'checking existence of key %s' %(key_suffix_credits)
                
                if self.redisconn.zrange(key_suffix_credits, 0, -1):
                    
                    # delete zero_credit_date. should not exist
                    
                    self.redisconn.hdel(key_suffix,
                        self.key_zero_credit_date)
                
                else:
                    
                    # obtains the date when the suffix credits became 0
                    
                    print 'obtaining %s from %s' %(key_suffix, 
                        self.key_zero_credit_date)
                       
                    zero_credit_date = self.redisconn.hget(
                        key_suffix, self.key_zero_credit_date)
                     
                    print 'zero credit date: %s ' %str(zero_credit_date)
                    
                    if zero_credit_date:

                        zcd_with_grace_period = self.compute_date_with_grace_period(
                            zero_credit_date, grace_period_in_days)
                        
                        print 'zero credit date plus grace period: %s ' %(
                            str(zcd_with_grace_period))
                        
                        if zcd_with_grace_period < datetime.datetime.now():
                            # may delete
                            
                            print 'zero credit date plus grace period > date now'
                            print 'DELETE this suffix'
                            
                            self.delete_suffixes(suffixes_info=suffixes_info, 
                                status=status, grace_period_in_days=grace_period_in_days,
                                zero_credit_date=zero_credit_date)                   
                   
            except Exception, e:
                import traceback
                print traceback.format_exc()
                print e
            
    
    def compute_date_with_grace_period(self, date, grace_period_in_days):
        '''
            @description:
                - returns the date with grace period
        '''

        date = datetime.datetime.strptime(
            date, '%Y-%m-%d %H:%M:%S')
                        
        return (date + datetime.timedelta(
            days=grace_period_in_days) + datetime.timedelta(hours=23)
            + datetime.timedelta(minutes=59) + datetime.timedelta(seconds=59))
            
          
