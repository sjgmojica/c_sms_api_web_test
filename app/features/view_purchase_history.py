'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from models.checkout import Checkout
from models.shopping_cart import ShoppingCart as Cart

from . import purchase_history_checkout_items_per_page

def get_all_checkouts(account_id, page=1):
    '''
        @description:
            - returns all checkouts from table checkout
            with @param account_id
    '''
    return Checkout.get_all_purchase_history(account_id, limit=purchase_history_checkout_items_per_page, page=page)

def get_all_checkout_ids(checkout_dicts):
    '''
        @param checkout_dicts: <dict>
        @description:
            - returns all checkout_ids of 
            extracted from checkout_dicts
            - used for generating individual
            checkout_items history report
    '''
    checkout_ids = []
    for checkout in checkout_dicts:
        checkout_ids.append(checkout['checkout_id'])
    return checkout_ids
    
def get_all_checkout_items(checkout_ids):
    '''
        @param checkout_ids: <list>
        @description:
            - returns all checkout items
            given their checkout_ids
    '''
    checkout_items = []
    for ids in checkout_ids:
        checkout_items.append(Cart.get_checkout_items(ids))
    return checkout_items


def get_purchase_history_items( checkout_id ):
    '''
    feature function used to retrieve checkout items
    
    '''
    
    try:
        items = Checkout.get_items( checkout_id = checkout_id )
        ph_items = {'result': True, 'data': items}
        
    except Exception, e :
        print 'exception rasied in feature', e
        items = []
        ph_items = {'result': False, 'data': items}
        
    
    return ph_items
    
    
    
def get_total_page_count( account_id ):
    '''
    retrieves total number of pages of purchase history
    
    '''
    
    total_pages = Checkout.get_purchase_history_page_count( account_id=account_id, items_per_page=purchase_history_checkout_items_per_page )
    return total_pages
    
    

def get_purchase_history_by_page( page ):
    
    
    purchase_history = []
    
    
    
    purchase_history.append( 
                            {'summary': {
                                         'id' : 1,
                                         'date':'date',
                                         'total': 1234.00,
                                         'paymentmode' : 'dragon',
                                         'status':'SUCCESS'
                                         }, 
                             
                             'items':[  
                                      {'code':'pla 500', 'qty': 1 , 'amt': 100},
                                      {'code':'pla 100', 'qty': 3 , 'amt': 300}
                                        
                                      ]  
                             }
                            
                            )
    
    
    
    return purchase_history
    
    
    
    
    