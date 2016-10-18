'''
    @author: Jhesed Tacadena
    @description:
        - handles viewing of purchase history
    @date: 2013-10
'''

from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from features.view_purchase_history import *


import ujson as json

@route(['/history/purchase', '/history/purchase/'])
class PurchaseHistoryRenderer(BaseHandlerSession):
 
    @authenticated
    @asynchronous
    def get(self):
        account_obj = self.get_current_user()
        checkouts = None
        checkout_items = None
        page_count=1
        try:
            # get total page count
            page_count = get_total_page_count( account_id=account_obj.account_id )
            checkouts = get_all_checkouts(account_obj.account_id)
#             checkout_ids = get_all_checkout_ids(checkouts)
#             checkout_items = get_all_checkout_items(checkout_ids)
        
        except Exception, e:
            print 'error in initializing purchase history page', e
            # self.finish() # ! TEMP !
        
        print 'using page count', page_count
        self.render('purchase_history.html',
            checkouts=checkouts, page_count=page_count)
        
@route('/history/get-page/([0-9]{1,4})')        
class PurchaseHistoryPageAjax( BaseHandlerSession ):

    @authenticated
    @asynchronous
    def get(self, page_number ):
        
        try:
        
            page_number = int(page_number)
        
            account_obj = self.get_current_user()
            
            result = {'result': True, 'data': 
                      
                                     [ { 'checkout_id': x['checkout_id'], 
                                        'date_purchased': x['date_purchased'].strftime('%m/%d/%Y'), 
                                        'amount':x['amount'],   
                                        'mode_of_payment': x['mode_of_payment'],
                                         'status': x['status'], 
                                         'webtool_reference_id': x['webtool_reference_id']   } for x in   get_all_checkouts(account_obj.account_id, page=page_number) ]
                      
                       }
        
        except Exception, e:
            result = {'result': False }
        
        self.write( json.dumps(result) )
        
        self.finish()
        
@route('/history/get-items/trans_([0-9]+)')                   
class AjaxGetPurchaseHistoryItems( BaseHandlerSession ):
    '''
    this handler accepts checkout id to retrieve checkout items
    from database. this is the ajax version, json string is returned
    '''
    @authenticated
    @asynchronous
    def get(self, checkout_id ):
        
        #sanitize checkout id
        try:
            checkout_id = int(checkout_id) 
            result = get_purchase_history_items( checkout_id )
        except Exception, e:
            print 'exception rasied', e
            result = {'result': False}
            
        self.write( json.dumps(result) )
        self.finish()
    
    