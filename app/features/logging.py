'''
sms api logging feature

logging classes for sms api


@author: vincent agudelo

'''

import fluent_logging_util.fluent_logging as fluent_logging 
import random


class SMSAPILogger( object ):
    
    f_sender = None
    trans_id = None
    
    def __init__(self):
        # auto generate transaction id for the life of the logger
        self.__generate_trans_id()
        
        self._load_sender()
    
    def regenerate_new_trans_id(self):
        '''
        in cases where one would want to create a new transaction id in the life time of
        this object
        
        '''
        self.__generate_trans_id()
    
    def __generate_trans_id(self):
        
        transid_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        self.trans_id = ''.join( random.choice( transid_chars ) for x in range(6) )

    
    def info(self, message='', data=None):
        self.__send('INFO',message=message, data=data)
        
    def error(self, message='', data=None):
        self.__send('ERROR',message=message, data=data)

    def debug(self, message='', data=None):
        self.__send('DEBUG',message=message, data=data)        

    def __send(self, tag, message='', data=None ):
        # saniize mssge
        # aniie dat too
        if type(message) is not str :
            message = repr(message)
            
        if data is not None:
            if type(data) is not str :
                data = repr(data)
            
        content = { 'trans_id':self.trans_id,   'msg': message, 'data': data }
        fluent_logging.fluent_send( 
                               f_sender=self.f_sender, 
                               tag=tag, 
                               content=content )


class PaymentLogger( SMSAPILogger ):
    def _load_sender(self):
        self.f_sender = fluent_logging.f_payment_sender
        
class SCartLogger( SMSAPILogger ):
    def _load_sender(self):
        self.f_sender = fluent_logging.f_shopping_cart_sender
        
class GeneralLogger( SMSAPILogger ):
    def _load_sender(self):
        self.f_sender = fluent_logging.f_general_sender

