'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
'''

from base_suffix_updater import BaseSuffixUpdater
import features.logging as sms_api_logger

class FreeSuffixUpdater(object):

    def main(self):
        '''
            @description:
                - encapsulates the whole free
                suffix updating process
        '''
        bs = BaseSuffixUpdater()
        bs.init()  # initializes base conns and configs
        suffixes_info = bs.select_suffix(package='FREE', days=30)
       
        print '\nfree suffixes dict: ' 
        print suffixes_info
        print '\n'
        
        su_logger = sms_api_logger.StandAloneSuffixFreeToInactiveLogger() 
        su_logger.info('START.', {'category': 'FREE TO INACTVE ' } )
        
        bs.delete_suffixes(suffixes_info=suffixes_info,
            status='PENDING', grace_period_in_days=30, 
            category='FREE_TO_INACTIVE')
          
        su_logger.info('END.', {'category': 'FREE TO INACTVE ' } )
            
def start_suffix_free_updater():
    '''
        @description:
            - calls FreeSuffixUpdater.main()
            to process updating of suffix
            where package=FREE
    '''
    fsu = FreeSuffixUpdater()
    fsu.main()