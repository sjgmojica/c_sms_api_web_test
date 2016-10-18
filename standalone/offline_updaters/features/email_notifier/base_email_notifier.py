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
from utils.send_mailx import send_mailx

EMAIL_SPIEL ='%s (%s) days before your Short Code expires. Sign in <a href="https://api.chikka.com/signin">here</a> to %s your Chikka API account%s'

class BaseEmailNotifier(object):
    
    dbconn = None
    redisconn = None    
        
    query_del_from_claimed_suffix = """delete from claimed_suffixes where account_id='%s'"""
    query_del_from_accounts = """update accounts set suffix=NULL where id='%s'"""
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
            
            
            self.mailer_settings = {
                'host': values['mailer']['host'], 
                'port': values['mailer']['port'], 
                'from_address': values['mailer']['mail_from_address'] 
            }
            
            print '-------'
            print 'sql:'
            print 'port: %s' %values['mysql-db']['sms_api_config']['host']
            print 'host: %s' %values['mysql-db']['sms_api_config']['port']
            print 'db: %s' %values['mysql-db']['sms_api_config']['db']
            print 'user: %s' %values['mysql-db']['sms_api_config']['user']
            print 'password: %s' %values['mysql-db']['sms_api_config']['password']
            print '-------'
                
                
    def select_suffix(self, days_interval, status='ACTIVE', package='FREE', suffix=''):
        '''
            @description:
                - returns a list of ids and suffixes based
                from the params passed
        '''
        # query = """select a.id, a.suffix, b.date_created from accounts as a,
            # claimed_suffixes as b where a.status = '%s' and a.package = '%s'
            # and a.suffix = b.suffix and a.id = b.account_id 
            # and b.date_created= (b.date_created + INTERVAL %s DAY)"""  %(
            # status, package, days_interval)
        
        query = """select a.id, a.suffix, a.email, b.date_created from accounts as a,
            claimed_suffixes as b where a.status = '%s' and a.package = '%s'
            and a.suffix = b.suffix and a.id = b.account_id 
            and month(now()) = month(b.date_created + INTERVAL %s DAY) and
            day(now()) = day(b.date_created + INTERVAL %s DAY) and
            year(now()) = year(b.date_created + INTERVAL %s DAY)"""  %(
            status, package, days_interval, days_interval, days_interval)

        
        print '\n - select suffix QUERY: - \n'
        print ' '.join(query.split())
        
        try:
            return self.dbconn.run_query(query_type='select', query=query,
                fetchall=True)
        except Exception, e:
            print e
        return None
    
   
    def send_email(self, to_address, shortcode, days_before_expiration):
        '''
            @description:
                - sends an information email
                to users with expiring short code
        '''
                
        body = EMAIL_SPIEL
        
        if str(days_before_expiration) == 'Thirty':
            body = body % (days_before_expiration, '30', 'replenish', '.')
        elif str(days_before_expiration) == 'Fourteen':
            body = body % (days_before_expiration, '14', 'replenish', '.')
        elif str(days_before_expiration) == 'Seven':
            body = body % (days_before_expiration, '7', 'upgrade', 
                ' and keep your short code.')
        
        subject = 'Reminder about your Chikka API short code' 
        
        return send_mailx(
            text_content=body, 
            html_content=body, 
            subject=subject, 
            to_=to_address,
             
            email_from_=self.mailer_settings['from_address'],
            mail_host=self.mailer_settings['host'], 
            mail_port=self.mailer_settings['port']
        )
    
    
    def send_confirmation_email(self, to_address, free_details,
        paid30_details, paid14_details):
        '''
            @description:
                -
        '''
        subject = '[Chikka SMS API] Email successfully sent confirmation' 
        body = 'Please see details below'
        
        body += '<br/><br/>FREE accounts (7 days before expiration)<br/>'
        body += str(free_details)
           
        body += '<br/><br/>PAID accounts (30 before expiration)<br/>'
        body += str(paid30_details)
           
        body += '<br/><br/>PAID accounts (14 before expiration)<br/>'
        body += str(paid14_details)
        
        return send_mailx(
            text_content=body, 
            html_content=body, 
            subject=subject, 
            to_=to_address,
             
            email_from_=self.mailer_settings['from_address'],
            mail_host=self.mailer_settings['host'], 
            mail_port=self.mailer_settings['port']
        )
        
       
    # --- functions to validate expiration of shortcodes ---
    
    def is_paid_suffix_expiring(self, grace_period_in_days, suffix):   
        
        key_suffix = self.key_cached_suffix % suffix
        
        zero_credit_date = self.redisconn.hget(
            key_suffix, self.key_zero_credit_date)
             
        print 'zero credit date: %s ' %str(zero_credit_date)
        
        if not zero_credit_date:
            return False
        
        if zero_credit_date:

            zcd_with_grace_period = self.compute_date_with_grace_period(
                zero_credit_date, grace_period_in_days)
            
            
            print 'zero credit date plus grace period: %s ' %(
                str(zcd_with_grace_period))
            
            if zcd_with_grace_period < datetime.datetime.now():
                # may delete
                
                print 'zero credit date plus grace period > date now'
                print 'THIS EMAIL SHOULD receive email notification'
                
                return True
            
            else:
                return False
                
                
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
            
          
