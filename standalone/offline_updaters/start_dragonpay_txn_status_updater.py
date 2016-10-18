'''
    @author: Jhesed Tacadena
    @description:
        - checks status of dragonpay transaction
        every x minutes (using txn_id)
        - updates neccessary DB 
        depending on status of txn
'''

import gevent

from features.dragonpay.dragonpay import Dragonpay

if __name__ == '__main__':
    try:
        dp = Dragonpay()
        gevent.spawn(dp.main).join()
    except Exception, e:
        import traceback
        print traceback.format_exc()