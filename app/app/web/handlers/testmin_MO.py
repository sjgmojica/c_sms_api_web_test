from ujson import dumps
from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from features.testmin.testmin_MO import \
    get_mo_obj, save_mo_message
from features.testmin.spiels import SPIELS

DEFAULT_MESSAGE = 'Hello, this is a sample MT message'
SENT_TRIAL_MESSAGE = 118  # 160 - len(SENT_TRIAL_MESSAGE)
    
    
@route(['/testmo', '/testmo/'])
class TestminSendHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def get(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
        
        mo_obj = get_mo_obj(account_id)
        mo_message = mo_obj['message']
        if not mo_message:
            mo_message = DEFAULT_MESSAGE

        else:
            # removes STM for display purpose
            mo_message = mo_message[len(SENT_TRIAL_MESSAGE)-2:] 
                              
        self.render('test_receive.html', 
            mo_message=mo_message,
            mo_testmin=mo_obj['testmin'])
        
@route(['/testmo/save', '/testmo/save/'])
class TestminSendMOHandler(BaseHandlerSession):
    
    @authenticated
    @asynchronous
    def post(self):
        account_obj = self.get_current_user() 
        account_id = account_obj.account_id
        
        if account_obj.package != 'FREE':
            self.redirect('/')
      
        # mo_testmin = self.get_argument('testmin')
        mo_testmin = account_obj.test_min
        
        if not mo_testmin:
            self.finish(dumps({'message': 'Invalid Mobile Number', 'error': True}))
            return
                
        mo_msg = self.get_argument('MO_message', None)
        is_successful = save_mo_message(account_id, mo_msg)       
        
        if not is_successful:
            self.finish(dumps({'message': 'invalid mo reply', 'error': True}))
            return 
        
        result = {
            'message': SPIELS['tempsuccess2'],
            'error': False
        }
        
        self.finish(dumps(result))
        
        # self.render('verify_number_enroll.html',
            # response=SPIELS['tempsuccess2'], testmin=mo_testmin,
            # message_id=None, mo_message=mo_msg)
            
        # self.render('test_receive.html', 
            # mo_message=mo_msg,
            # mo_testmin=mo_testmin)
        