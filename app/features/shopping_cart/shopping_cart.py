'''
    @author: Jhesed Tacadena
    @description:
        - shopping_cart feature contains functions
        which are used when interacting with
        the shopping cart. (called by handlers i.e. diff platforms)
        - These raise custom exceptions which
        are caught by the calling handlers to produce
        necessary actions (i.e. spiels)
    @date: 2013-10
'''

from datetime import datetime, timedelta
from ast import literal_eval
from models.shopping_cached_cart import ShoppingCachedCart as CachedCart
from models.shopping_cart import ShoppingCart as Cart
from models.account import Account
from models.suffixes import Suffixes
from models.dragonpay import Dragonpay
from models.checkout import Checkout, SmartPaymentGatewayCheckout, CheckoutNotExistError, CheckoutExpiredError

from features.shopping_cart.packages import *
from features.shopping_cart.exceptions import *
from features.shortcode.exceptions import NoSuffixException
import features.logging as sms_api_logger
from utils.mobile_formatting_util import is_mobile_format_valid, \
    InvalidMobileFormatException, MobileNotSmartException
from utils.determine_carrier import DetermineCarrier
from utils.code_generation import generate_code

from features.payments.dragonpay.dragonpay import is_allowed_for_amount as dp_is_allowed_for_amount 
    
from features.paypal import paypal_main  
from features.paypal.paypal_checkout_model import PaypalPaymentCheckout


MESSAGE_PINCODE = 'hello. Your verification code is %s. Please input it in your browser'
MAX_PINCODE_TRIES = 3
PINCODE_EXPIRATION = 30 # in minutes

def get_cart_items(account_id):
    '''
        @param account_id: the account id of the user 
            obtained from logging in
        @description:
            - returns the cart of the user for
            viewing purpose
    '''

    scart_logger = sms_api_logger.SCartLogger()    
    # scart_logger.info('obtaining cart items', {'account_id' : account_id})
    
    if not Suffixes.is_user_has_suffix(account_id):
        # scart_logger.error('user has no suffix', {'account_id' : account_id})
        raise NoSuffixException(account_id)
    
    cached_cart = CachedCart.get_items(account_id) or []
    
    if not cached_cart:
        # scart_logger.error('cart is empty', {'account_id' : account_id})
        raise CartEmptyException(account_id)
        
    # trims the needed details for frontend printing
    
    cached_cart_trimmed = []
    for c in cached_cart:
        # to prevent hacking (it sec, package details are injected here)
        __fill_package_details(c) 
        
        temp = {
            'amount': c['amount'],
            'id': c['id'],
            'plan_code': c['plan_code'],
            'quantity': c['quantity']
        }
        cached_cart_trimmed.append(temp)
        
    
    # scart_logger.info('success obtaining cart', {'account_id' : account_id})
    return cached_cart_trimmed

def get_cart_items_count(account_id):
    '''
        @description:
            - returns count of items in cart
    '''
    
    # scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('obtaining cart items COUNT', {'account_id' : account_id})
    
    if not Suffixes.is_user_has_suffix(account_id):
        # scart_logger.error('user has no suffix', {'account_id' : account_id})
        raise NoSuffixException(account_id)
    
    cached_cart = CachedCart.get_items(account_id)
    if not cached_cart:
        return 0
    
    # scart_logger.info('success obtaining cart count', {'account_id' : account_id})
    return len(cached_cart)
    
        
def add_update_cart(account_id, new_data, type='system_generated'):
    '''
        @param account_id: the account id of the user 
            obtained from logging in
        @param new_data: (dict)
        @param type: (system_generated | user_generated)
            - if system_generated, quantity will be updated
                by adding the new quantity to the existing
                (used when adding to cart)
            - if user_generated, quantity will be the 
                new quantity
                (used when user modifies the quantity
                directly when viewing the cart)
        @description:
            - adds @param new_data to user's cart
    '''
    
    
    scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('START -- adding/updating cart', {'account_id' : account_id})
    
    cached_cart = CachedCart.get_items(account_id) or []
        
    # if the plan is not yet in the cart
    
    if not cached_cart or (not int(new_data['id']) in map(
        lambda x: int(x['id']), cached_cart)):
        
        __fill_package_details(new_data) # fills details for package data 
        
        if new_data:
            cached_cart.append(new_data)
        
            scart_logger.info('adding NEW item to cart', 
                {'account_id' : account_id, 'item_id': new_data['id'],
                'plan_code': new_data['plan_code']})   
    else:
        existing_index = None
        for i, v in enumerate(cached_cart):
            if v and 'id' in new_data and int(v['id']) == int(new_data['id']):
                existing_index = i
                
        if existing_index is not None: # 0 is treated as not
        
            # scart_logger.info('adding quantity to EXISTING item in cart', 
                # {'account_id' : account_id, 'item_id': new_data['id']})
         
            # used when adding to cart
            
            if type == 'system_generated':
                scart_logger.info('system generated -- updating EXISTING cart item quantity', 
                    {'account_id' : account_id, 'item_id': new_data['id']})
                sum = int(cached_cart[existing_index]['quantity']) + int(new_data['quantity'])
                cached_cart[existing_index]['quantity'] = sum
            
            # used when user is modifying the quantities in view cart 
            
            elif type == 'user_generated':
                scart_logger.info('user generated -- updating EXISTING cart item quantity',
                    {'account_id' : account_id, 'item_id': new_data['id']})
                cached_cart[existing_index]['quantity'] = int(new_data['quantity'])
        else:
            cached_cart.append(new_data)

    # scart_logger.info('success adding item/updating cart', {'account_id' : account_id})
    CachedCart.save_item_to_cart(account_id, cached_cart)
    
    return cached_cart

def wipe_out_cached_cart(account_id):
    '''
        @description: 
            - wipes out the shopping cart
            with @param account_id
    '''
        
    scart_logger = sms_api_logger.SCartLogger()
    scart_logger.info('wiping cart', {'account_id' : account_id})           
    return CachedCart.wipe_out_cart(account_id)  

def delete_from_cart(account_id, plan_id):
    '''
        @description:
            - adds @param new_data to user's cart
    '''
    
    scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('START -- deleting item in cart', {'account_id' : account_id})           
   
    cached_cart = CachedCart.get_items(account_id) or []
    existing_index = None
    
    if cached_cart:
        for i, v in enumerate(cached_cart):
            if int(v['id']) == int(plan_id):
                existing_index = i
                
        # deletes the item from cart where id == plan_id
        
        if existing_index is not None: # 0 is treated as not
            scart_logger.info('deleting cart item with ID', 
                {'account_id' : account_id, 'item_id': plan_id})           
            cached_cart.pop(existing_index)
   
    # else:
        # scart_logger.info('cart is empty', {'account_id' : account_id})           
        
    # deletes the cart item by saving updated cart
    
    CachedCart.save_item_to_cart(account_id, cached_cart)
    return cached_cart

def checkout_cart(account_id, updated_plan_quantities):
    '''
        @param account_id: the account id of the user 
            obtained from logging in
        @param updated_plan_quantities: (list)
        @description:
            - checkouts cart.  The items in cart
            may be changed depending on @param 
            updated_plan_quantities. 
            - This function ensures that the user
            modified package quantities will
            match the cart after checking out
    '''
    
    # scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('reupdating cart based on user generated quantity input',
        # {'account_id' : account_id})           
    
    for pq in updated_plan_quantities:
        # updates the record in cache based on the
        # user inputted new quantities in plan
        try:   
            add_update_cart(account_id, literal_eval(pq), 'user_generated')
        
        except Exception, e:
            pass # for ast.literal_eval
                
    return get_cart_items(account_id)
    
def process_smart_payment_authentication(account_id, mobile, amount):
    '''
        @description:
            - processes smart gateway
            authentication.  Used when the user inputs
            his/her mobile number for payment.
            - this function:
                + generates a random code
                + transfer the redis cart items to DB
                + sends the pincode to the user
    '''
    
    
    scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('START -- smart payment mobile num authentication', 
        # {'account_id' : account_id, 'mobile': mobile, 'amount': amount})           
    
    if not is_mobile_format_valid(mobile):
        scart_logger.error('SMART payment MOBILE -- invalid mobile', 
            {'account_id' : account_id, 'mobile': mobile})           
        raise InvalidMobileFormatException(mobile)
    
    # format to 63XXXXXXXXXX
    mobile = '63%s' % mobile[-10:]
    
    # is mobile smart ?
    
    dt = DetermineCarrier(mobile)
    if dt.get_carrier() != 'SMART':
        scart_logger.error('SMART payment MOBILE -- mobile not smart', 
            {'account_id' : account_id, 'mobile': mobile})           
        raise MobileNotSmartException(account_id, mobile)
    
    rand_code = generate_code()
    # scart_logger.info('generating random code', 
        # {'account_id' : account_id, 'code': rand_code})
    
    checkout_id = __save_cart_items_from_cache_to_db(account_id, mobile, rand_code, amount)
    wipe_out_cached_cart(account_id)
    
    # build lightweight smart payment checkout object to send code via sms
    checkout_object = SmartPaymentGatewayCheckout()
    checkout_object.checkout_id = checkout_id

    checkout_object.code = rand_code
    checkout_object.phone = mobile
    message_id = checkout_object.send_payment_PIN_code()

    scart_logger.info('SMART payment MOBILE -- sending pincode to user', 
        {'account_id' : account_id, 'mobile': mobile, 'code': rand_code, 'message_id': message_id})    

    return checkout_id
    
def process_smart_payment_verification(account_id, pincode, checkout_id):
    '''
        @description:
            - processes the pincode verification based
            from smart payment.
            - pushes the succesfful verification
            to checkout_queue (redis) for payment process
    '''
    
    scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('START -- checkout cart pincode verification', 
        # {'account_id' : account_id, 'checkout_id': checkout_id, 'code': pincode})           
        
    #cart_checkout = Cart.get_checkout(account_id, checkout_id)
    
    cart_checkout = Checkout.get( checkout_id = checkout_id )
    
    if not cart_checkout:
        scart_logger.error('SMART payment PINCODE -- cant pay. cart is empty', 
            {'account_id' : account_id, 'checkout_id': checkout_id})           
    
        raise CartEmptyException(account_id)
        
    """
    if cart_checkout.retry_ctr >= MAX_PINCODE_TRIES:
        raise MaxCodeRetriesException(account_id, pincode)
    """
       
    if not __is_pincode_correct(cart_checkout.code, pincode):
        scart_logger.error('SMART payment PINCODE -- incorrect pincode', 
            {'account_id' : account_id, 'checkout_id': checkout_id})           
    
        # Cart.incr_retry_ctr(checkout_id)
        raise IncorrectPincodeException(account_id, pincode)
        
    if __is_pincode_expired(cart_checkout.date_expiry):
        scart_logger.error('SMART payment PINCODE -- expired pincode', 
            {'account_id' : account_id, 'checkout_id': checkout_id})           
    
        # sets expired to 1, to avoid date recomputations in future
        Cart.update_checkout_expired(checkout_id) 
        raise ExpiredPincodeException(account_id, pincode)
    
    Cart.update_checkout_status_to_pending(checkout_id)
    cart_checkout.status = Checkout.STATUS_PENDING
    
    was_push_successful = CachedCart.push_to_checkout_queue(checkout_id)
    
    # write to purchase history
    #cart_checkout.write_to_purchase_history()
    try:
        cart_checkout.write_pending_purchase_history()
    except Exception, e:
        scart_logger.error('suppress error in writing purchase history. duplicate record may already exist', {'checkout_id':checkout_id} )
    
    
    
    if not was_push_successful or int(was_push_successful) == 0:
        scart_logger.error('SMART payment PINCODE -- pushing to checkoutqueue for payment -- NOT successful', 
            {'account_id' : account_id, 'checkout_id': checkout_id})           
    
        raise CheckoutQueuePushException(account_id, checkout_id)
    
    scart_logger.info('SUCCESS -- checkout cart pincode verification', 
        {'account_id' : account_id, 'checkout_id': checkout_id, 'code': pincode})           
    
    
def process_dragonpay_checkout(account_id, amount):
    '''
        @description: 
            - processes checkout for dragonpay
        @param account_id:  account id of user
        @param txn_id:  
    '''
    
    # before doing anything, double check if
    # amount is within minimum amount
    if dp_is_allowed_for_amount( amount ):
        scart_logger = sms_api_logger.SCartLogger()
        
        # --- saves checkout to DB and deletes in cache ---
        
        # some fields are not necessary for dragonpay checkout
        checkout_id = __save_cart_items_from_cache_to_db(
            account_id=account_id, phone='', code='', 
            amount=amount, mode_of_payment='DRAGONPAY', 
            status='PENDING')
        wipe_out_cached_cart(account_id)
        return checkout_id
    else:
        raise Exception( 'amount %s is not allowed for dragonpay' % amount )



def process_paypal_checkout(account_id, amount):
    '''
    @authr: vincet agudelo
    @description: generates checkout record paypal as mode of payment
    @param account_id:  account id of user
    @param txn_id:  
    '''
    
    
    #check if pending paypal payment exists
    
    
    existing_pending_paypal_payment_checkout = None
    try:
        existing_pending_paypal_payment_checkout = PaypalPaymentCheckout.get_paypal_pending_payment_flag( account_id )
        
        
    except Exception, e:
        raise ShoppingCartError('unable to check existing pending paypal payment: %s'%e)

    if existing_pending_paypal_payment_checkout:
        raise ShoppingCartError('Pending paypal payment exists. please wait 10 minutes to purchase another ')

    
    
    #check if amount is allowed for checkout
    
    amount_allowed = paypal_main.is_allowed_for_amount( amount=amount )
    if amount_allowed :
        scart_logger = sms_api_logger.SCartLogger()
        # --- saves checkout to DB and deletes in cache ---
    
    
        if paypal_main.is_within_allowed_paypal_purchases( account_id=account_id, amount=amount  ):
    
            checkout_id = __save_cart_items_from_cache_to_db(
                account_id=account_id, phone='', code='', 
                amount=amount, mode_of_payment='PAYPAL', status='PENDING')
            
            if checkout_id:
            
            
                ##########################
                # write purchase history
                ##########################
                
                # @todo make a cheaper way to get the checkout object
                
                checkout_object = Checkout.get( checkout_id = checkout_id )
                checkout_object.write_to_purchase_history()
                
                
                wipe_out_cached_cart(account_id)
                return checkout_id
            else:
                raise ShoppingCartError( 'no checkout generated, shopping cart might be empty' )
        else:
            
            raise paypal_main.PaypalPaymentError('maximum allowable paypal purchase per month reached', {'account_id':account_id, 'amount':amount, 'max': paypal_main.allowed_purchases_per_month })
            
    else:
        raise PaymentMethodError( 'amount %s is not allowed for payment method PAYPAL'% amount,  {'account_id':account_id, 'amount':amount}  )

##########################
# PAYMAYA CHECKOUT!!!
##########################
def process_paymaya_checkout(account_id, amount):
    '''
    @authr: sarz - makmakulet ;)
    @description: generates checkout record paymaya as mode of payment
    @param account_id:  account id of user
    @param txn_id:  
    '''
    
    scart_logger = sms_api_logger.SCartLogger()
    # --- saves checkout to DB and deletes in cache ---
    
    checkout_id = __save_cart_items_from_cache_to_db(
        account_id=account_id, phone='', code='', 
        amount=amount, mode_of_payment='PAYMAYA', status='PENDING')

    if checkout_id:
    
    
        ##########################
        # write purchase history
        ##########################
        
        # @todo make a cheaper way to get the checkout object
        
        checkout_object = Checkout.get( checkout_id = checkout_id )
        checkout_object.write_to_purchase_history()
        
        # wipe_out_cached_cart(account_id)
        return checkout_id
    else:
        raise ShoppingCartError( 'no checkout generated, shopping cart might be empty' )



def compute_total_amount(cart_items):
    '''
        @description:
            - computes total amount based on cart items
    '''
    total_cost = 0
    for item in cart_items:
        amount = float(item['amount']) * int(item['quantity'])
        total_cost += amount
    
    return total_cost    


def get_checkout_for_enter_code( account_id, checkout_id ):
    '''
    retrieves a checkout for the enter pin code screen
    
    this requires a non expired, null status (for payment) checkout and that
    the account id belongs to the specified account id
    
    raises exceptions
    
    '''
    
    checkout_object = get_non_expired_checkout( checkout_id=checkout_id )

    if checkout_object.account_id != account_id :
        raise Exception('current user trying to access checkout of another account')
    elif checkout_object.status:
        raise Exception( 'checkout is not for payment. status=%s' % checkout_object.status )

    return checkout_object
    
    

def get_non_expired_checkout( checkout_id ):
    
    
    try :
        checkout_object = Checkout.get( checkout_id=checkout_id )

    except Exception, e :
        raise Exception('failure in retrieving checkout: %s' % e )
        
    if not checkout_object:
        # not found in database
        # does not exist
        raise CheckoutNotExistError('not found in database')
    
   
    if checkout_object.date_expiry < datetime.now() :
        # of course you want an non-expired one , therefor this is an error
        raise CheckoutExpiredError( 'this checkout is expired' )
    
    return checkout_object


    
def __fill_package_details(new_data):
    details = get_package(new_data['id'])
 
    try:
        new_data['plan_code'] = details.plan_code
        new_data['plan_description'] = details.plan_description
        new_data['amount'] = details.amount
        new_data['days_valid'] = details.days_valid
    except Exception, e:
        # the only exception that will occur is when
        # the packages in package table was deleted
        # and switched to new packages
        print e
        
# --- FUNCTIONS ---
# --- USED BY ---
# --- PROCESS SMART_PAYMENT  ---
# --- AUTHENTICATION ---

def __save_cart_items_from_cache_to_db(account_id, phone, 
    code, amount, mode_of_payment='SMART', status=None):
    '''
        @description:
    '''
    
    # scart_logger = sms_api_logger.SCartLogger()
    # scart_logger.info('START -- saving cart items to DB', 
        # {'account_id' : account_id, 'mobile': phone, 'amount': amount,
        # 'mode_of_payment': mode_of_payment})           
    
    try:
        cached_cart = get_cart_items(account_id)
    
    except Exception, e:
        cached_cart = []
        
    if cached_cart:
    
        # saves to checkout table    
                
        checkout_dict = {
            'account_id': account_id,
            'phone': phone,
            'code': code,
            'date_expiry': datetime.now() + timedelta(
                minutes=PINCODE_EXPIRATION),
            'mode_of_payment' : mode_of_payment,
            'suffix': Suffixes.is_user_has_suffix(account_id),
            'amount': amount,
            'status': status
        }
                
        checkout_id = Cart.save_checkout(account_id, checkout_dict)
        
        # saves to checkout item table
            
        for cart in cached_cart:      
            cart['checkout_id'] = checkout_id
            Cart.save_checkout_items(cart)
            
        return checkout_id
    
    return None
     

# --- FUNCTIONS ---
# --- USED BY ---
# --- PROCESS SMART_PAYMENT  ---
# --- VERIFICATION ---

def __is_pincode_correct(correct_code, code):
    if str(correct_code).upper() == str(code).upper():
        return True
    return False
    
def __is_pincode_expired(date_expiry):
    if datetime.now() > date_expiry:
        return True
    return False

class ShoppingCartError( Exception ):
    pass