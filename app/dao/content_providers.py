'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from itertools import izip
from models.content_providers import ContentProviders
from datetime import datetime, timedelta
import features.logging as sms_api_logger

TABLE_CONTENT_PROVIDERS = 'content_providers'

REDIS_CONTENT_PROVIDERS = 'SMSAPI_%s'
REDIS_CONTENT_PROVIDERS_TRIAL_EXPIRATION = 2629743  # 1 month

TRIAL_CREDITS_KEY = 'TRIAL_CREDITS'
CREDITS_COUNT = 25


class ContentProvidersDao(object):
    
    def __init__(self, dbconn, redisconn):
        self.dbconn = dbconn
        self.redisconn = redisconn
        
   
    def get(self, suffix):
        KEY = REDIS_CONTENT_PROVIDERS % str(suffix)
        try:
            result = self.redisconn.hgetall(KEY)
            
            # converts list result of python hgetall to dict values
            if result:
                i = iter(result)
                result = dict(izip(i,i))
            
            return result
        except Exception, e:
            print e
            
        """
        # ! SQL VERSION DEPRECATED !
        
        criteria = {
            'suffix': suffix
        }
        
        table_cols = [
            'suffix',
            'public_key',
            'mo_endpoint',
            'dn_endpoint'
        ]
        
        try:
            result = self.dbconn.execute_select(
                table_name=TABLE_CONTENT_PROVIDERS,
                conditions=criteria,
                table_cols=table_cols,
                fetchall=False
            )
            
            if result:
                cp_object = ContentProviders()
                cp_object.suffix = result['suffix']
                cp_object.public_key = result['public_key']
                cp_object.mo_endpoint = result['mo_endpoint']
                cp_object.dn_endpoint = result['dn_endpoint']
                
                return cp_object
                
        except Exception, e:
            print e
            raise e
        
        return None
        """
        
    
    def create(self, suffix, **kwargs):
   
        params = {
            'suffix' : suffix
            # 'date_registered': datetime.now()
        }
        
        if 'public_key' in kwargs:
            params['public_key'] = kwargs['public_key']
        if 'mo_url' in kwargs:
            params['mo_endpoint'] = kwargs['mo_url']
        if 'callback_url' in kwargs:
            params['dn_endpoint'] = kwargs['callback_url']
        if 'testmin' in kwargs:
            params['test_min'] = ('639%s' %kwargs['testmin'][-9:])
            
            # date_registered and
            # time_registered should auto update
           
        try:
            return self.dbconn.execute_insert_update(
                table_name=TABLE_CONTENT_PROVIDERS, 
                insert_params=params, update_params=params)
   
        except Exception, e:
            print e
            
    def set_api_trial_credits(self, suffix):
        '''
            @description:
                - called when user buys a shortcode
                - sets api_trial settings to TRIAL_CREDITS
                in INFRA's redis
        '''
        
        gen_logger = sms_api_logger.GeneralLogger()    
        KEY = REDIS_CONTENT_PROVIDERS % str(suffix)
        
        try:
            self.redisconn.hset(KEY, TRIAL_CREDITS_KEY,
                str(CREDITS_COUNT))
            self.redisconn.hset(KEY, 'ACTIVE',
                str(2))
            # self.redisconn.hset(KEY, 'TEST_MIN',
                # str(('639%s' %kwargs['testmin'][-9:])))
                        
            # self.redisconn.expire(KEY,
                # REDIS_CONTENT_PROVIDERS_TRIAL_EXPIRATION)
            
            gen_logger.info('updating TRIAL CREDITS', {'suffix': suffix})
            
        except Exception, e:
            gen_logger.error('error updating TRIAL CREDITS', 
                {'suffix': suffix, 'error': str(e)})
            print e
     
    def update_cached_api_min(self, suffix, min):
        
        gen_logger = sms_api_logger.GeneralLogger()    
         
        try:
            KEY = REDIS_CONTENT_PROVIDERS % str(suffix)
            self.redisconn.hset(KEY, 'TEST_MIN',
                str(('639%s' %min[-9:])))
            gen_logger.info('updating TESTMIN in API', 
                {'suffix': suffix, 'testmin': min})
        except Exception, e:
            gen_logger.error('error updating TESTMIN in API', 
                {'suffix': suffix, 'testmin': min})
            print e
                
    def update_cached_api_settings(self, suffix, **kwargs):
        '''
            @description:
                - inserts to INFRA's redis for 
                API usage
        '''
        
        data = {}
        
        if 'client_id' in kwargs:
            data['CLIENT_ID'] = kwargs['client_id']
        if 'secret_key' in kwargs:
            data['SECRET_KEY'] = kwargs['secret_key']
        if 'public_key' in kwargs:
            data['PUBLIC_KEY'] = kwargs['public_key']
        if 'mo_url' in kwargs:
            data['MO_ENDPOINT'] = kwargs['mo_url']
        if 'callback_url' in kwargs:
            data['DN_ENDPOINT'] = kwargs['callback_url']
        if 'active' in kwargs:
            data['ACTIVE'] = kwargs['active']
        
        """
        data = {
            'PUBLIC_KEY' : kwargs['public_key'],
            # 'TEST_MIN' : str(('639%s' %kwargs['testmin'][-9:])),
            'MO_ENDPOINT' : kwargs['mo_url'],
            'DN_ENDPOINT' : kwargs['callback_url']
            # 'ACTIVE': str(2) # 2 for TRIAL
         
            # 'TRIAL_CREDITS' : 20  # to consult
        }
        """
        
        gen_logger = sms_api_logger.GeneralLogger()    
        KEY = REDIS_CONTENT_PROVIDERS % str(suffix)
        
        try:
            for key in data:
                self.redisconn.hset(KEY, key, data[key])
        
            gen_logger.info('updating API settings', {'suffix': suffix})
        except Exception, e:
            gen_logger.error('error updating API settings', 
                {'suffix': suffix, 'error': str(e)})
            print e