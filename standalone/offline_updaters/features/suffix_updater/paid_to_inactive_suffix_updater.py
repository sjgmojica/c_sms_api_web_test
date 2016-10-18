'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
'''

from base_suffix_updater import BaseSuffixUpdater
import features.logging as sms_api_logger

class PaidToInactiveSuffixUpdater(object):

    def main(self):
        '''
            @description:
                - encapsulates the whole free
                suffix updating process
        '''
        bs = BaseSuffixUpdater()
        bs.init()  # initializes base conns and configs
        suffixes_info = bs.select_suffix(package='PAID', days=60)
       
        print '\npaid to inactive suffixes dict: ' 
        print suffixes_info
        print '\n'
        
        su_logger = sms_api_logger.StandAloneSuffixPaidToInactiveLogger() 
        su_logger.info('START.', {'category': 'PAID TO INACTVE ' } )
        
        bs.delete_expired_suffixes_with_zero_credits(
            suffixes_info=suffixes_info,
            status='PENDING', grace_period_in_days=90)
          
        su_logger.info('END.', {'category': 'PAID TO INACTVE ' } )
            
def start_suffix_paid_to_inactive_updater():
    '''
        @description:
            - calls FreeSuffixUpdater.main()
            to process updating of suffix
            where package=FREE
    '''
    fsu = PaidToInactiveSuffixUpdater()
    fsu.main()