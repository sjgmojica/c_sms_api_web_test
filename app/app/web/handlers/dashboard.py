from tornado.web import authenticated, asynchronous
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

from models.checkout import Checkout

from features.account_management import transaction_history_viewer

@route('/')
class WebFrontLandingPageHandler( BaseHandlerSession ):
    
    @asynchronous
    def get(self):
        '''
        simple handler that displays the landing page
        nothing special
        '''
        
        if self.get_current_user() :
            self.redirect( '/dashboard' )
        else:
            self.render('landing_page.html')
        
        return
        



@route(['/dashboard', '/dashboard/'])
class SignupVerificationHandler( BaseHandlerSession ):
    
    @authenticated
    def get(self):
        
        notification = None
        notification_type = self.get_argument('notif-type', None)
        
        if notification_type == 'smart-payment-confirmed':
            notification = 'Thank you for your purchase. We will now process this transaction. A confirmation message will be sent once your payment is received.'

        try :
            rates = Checkout.get_carrier_charging()
        except Exception, e :
            print 'unable to load rates: %s' % e
            dashboard_sms_rates=''

        recent_transactions = {'inbox': [],'sent' : []}
        try :
            recent_transactions['inbox'] = transaction_history_viewer.get_latest_mo_transactions( account_object=self.current_user )
            recent_transactions['sent'] = transaction_history_viewer.get_latest_mt_transactions( account_object=self.current_user )
        except Exception, e:
            print 'exception raised %s' % e
            


        
        self.render('dashboard.html',
                    transactions = recent_transactions, 
                    rates=rates,
                    notification=notification)
        
        
        return
