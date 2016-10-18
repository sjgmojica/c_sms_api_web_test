'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
'''

from base_suffix_updater import BaseSuffixUpdater
import features.logging as sms_api_logger

class UnpaidToInactiveSuffixUpdater(object):

    def main(self):
        '''
            @description:
                - encapsulates the whole free
                suffix updating process
        '''
        bs = BaseSuffixUpdater()
        bs.init()  # initializes base conns and configs
        
        extra_query = '(b.date_created + INTERVAL 2 DAY) < now()'
        suffixes_info = bs.select_suffix(package='UNPAID',
            extra_query=extra_query)
       
        print '\nfree suffixes dict: ' 
        print suffixes_info
        print '\n'
        
        su_logger = sms_api_logger.StandAloneSuffixUnpaidToInactiveLogger()  
        su_logger.info('START.', {'category': 'UNPAID TO INACTVE ' } )
        
        bs.delete_suffixes(suffixes_info=suffixes_info,
            status='PENDING', grace_period_in_days=2,
            category='UNPAID_TO_INACTIVE')
        
        su_logger.info('END.', {'category': 'UNPAID TO INACTVE ' } )
                
def start_suffix_unpaid_to_inactive_updater():
    '''
        @description:
            - calls UnpaidToInactiveSuffixUpdater.main()
            to process updating of suffix
            where package=FREE
    '''
    fsu = UnpaidToInactiveSuffixUpdater()
    fsu.main()