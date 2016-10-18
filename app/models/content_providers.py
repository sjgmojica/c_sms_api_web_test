'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from datetime import datetime, timedelta

TABLE_CONTENT_PROVIDERS = 'content_providers'

class ContentProviders(object):
    
    dao = None
            
    @staticmethod
    def get(suffix, **kwargs):
        return ContentProviders.dao.get(
            suffix, **kwargs)
        
    @staticmethod
    def create(suffix, **kwargs):
        return ContentProviders.dao.create(
            suffix, **kwargs)
            
            
    @staticmethod
    def set_api_trial_credits(suffix):
        '''
            @description:
                - called when user buys a shortcode
                - sets api_trial settings in INFRA's redis
        '''
        return ContentProviders.dao.set_api_trial_credits(
            suffix)
    
    @staticmethod
    def update_cached_api_min(suffix, min):
        return ContentProviders.dao.update_cached_api_min(suffix, min)
    
    @staticmethod
    def update_cached_api_settings(suffix, **kwargs):
        '''
            @description:
                - inserts to INFRA's redis for 
                API usage
        '''
        return ContentProviders.dao.update_cached_api_settings(
            suffix, **kwargs)