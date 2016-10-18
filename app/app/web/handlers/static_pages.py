'''
static pages, nothing special nor related to the actual app

'''


from tornado.web import asynchronous
from app.web.handlers.web_base_handler import BaseHandlerSession as RequestHandler
from app.base.utils.route import route
from models.checkout import Checkout
from features.shopping_cart.packages import get_packages

@route(['/contact-us', '/contact-us/'])
class StaticContactUs( RequestHandler ):
    
    @asynchronous
    def get(self):
        
        self.render('contact_us.html')
        
        
        
@route(['/privacy', '/privacy/'])
class StaticContactUs( RequestHandler ):
    
    @asynchronous
    def get(self):
        
        self.render('privacy.html')
        
        
@route(['/terms-conditions', '/terms-conditions/'])
class StaticContactUs( RequestHandler ):
    
    @asynchronous
    def get(self):
        self.render('terms_conditions.html')
        
@route(['/help', '/help/'])
class StaticContactUs( RequestHandler ):
    
    @asynchronous
    def get(self):
        rates = Checkout.get_carrier_charging()
        self.render('help.html', rates=rates)
        
        
@route(['/ad-smsapi', '/ad-smsapi/'])
class StaticContactUs( RequestHandler ):
    
    @asynchronous
    def get(self):
        
        packages_list = get_packages()
        self.render('ad_smsapi.html', 
            packages_list=packages_list)