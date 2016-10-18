from ujson import dumps
from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from features.testmin.testmin_MT import *
import features.logging as sms_api_logger
    
@route(['/testmt', '/testmt/'])
class TestminMTHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
            
        testmin = get_testmin(account_id)
        self.render('test_send.html', testmin=testmin,
            message_id=None)
        
@route(['/testmt/send', '/testmt/send/'])
class TestminSendMTHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        
        account_obj = self.get_current_user() 
        
        testmin = account_obj.test_min
        response = self.get_argument('response', None)
        message_id = self.get_argument('mid', None)
        mo_message = account_obj.test_mo_reply
        
        self.render('verify_number_enroll.html',
            response=response, testmin=testmin,
            message_id=message_id, mo_message=mo_message)
            
    
    @authenticated
    @asynchronous
    def post(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
            
        mt_msg = self.get_argument('MT_message', None)
        mt_obj = get_mt_obj(account_id)   
             
        if not mt_obj['testmin']:

            self.redirect('/testmt/send?response=%s' %(
                'Invalid Mobile Number'))
            
            # self.render('verify_number_enroll.html',
                # response="Invalid Mobile Number", testmin=None,
                # message_id=None, mo_message=mt_obj['mo_reply'])
            
            return
        
        message_id = send_mt_message(account_id, mt_obj['suffix'], 
            mt_obj['testmin'], mt_msg, mt_obj['client_id'], mt_obj['secret_key'])
       
        if not message_id:
            self.finish(dumps({'error': True, 'message': 'Invalid message'}))
            return
            
        response = {
            'message_id' : message_id
        }
        
        self.redirect('/testmt/send?mid=%s' % message_id)
        
        # self.render('verify_number_enroll.html',
            # response=None, testmin=mt_obj['testmin'],
            # message_id=message_id, mo_message=mt_obj['mo_reply'])
            
        # self.finish(dumps(response))
        # self.render('test_send.html', testmin=mt_obj['testmin'],
            # message_id=message_id)
        
          
@route(['/message/sent', '/message/sent/'])
class PincodeSentVerifier(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
        
        mobile = self.get_argument('mobile', None)
        message_id = self.get_argument('message_id', None)
        
        if mobile and message_id:
            status = get_message_sent_status(mobile, message_id)
            
            if not status:
                status = 'FAIL'
            self.write(status)
        self.finish()

        
############################################        
######SHOULD NOT BE USED BY WEBTOOL#########
############################################

@route(['/message/sent/status', '/message/sent/status/'])
class PincodeSentCallbackHander(BaseHandlerSession):
    '''
        @description:
            - handles sms sent callback
            - updates status in redis upon successful sending
    '''
    
    @asynchronous
    def post(self):
        
        mobile = self.get_argument('mobile_number', None)
        message_id = self.get_argument('message_id', None)
        status = self.get_argument('status', None)
        gen_logger = sms_api_logger.GeneralLogger() 
        gen_logger.info('MT text CALLBACK HIT', 
            {'message_id': message_id, 'mobile': mobile})
        
        if not mobile or not message_id or not status:
            response = 'Error'
        
        elif status.lower() == 'sent':
            
            set_message_sent_to_success(mobile, message_id)
            response = 'Accepted'
        
        else:
            response = 'Error'
        
        # self.write(response)
        self.finish(response)
