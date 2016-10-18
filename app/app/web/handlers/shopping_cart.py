'''
    @author: Jhesed Tacadena
    @description:
        - calls shopping_cart feature to process
        cart operations.
        - renders custom error messages if the
        shopping cart feature raises exception(s)
    @date: 2013-10
'''

from tornado.web import asynchronous, authenticated
import json
from ujson import loads, dumps
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route
from models.checkout import Checkout, SmartPaymentGatewayCheckout
from features.shopping_cart.packages import get_packages
from features.shopping_cart.shopping_cart import *
from features.shopping_cart.exceptions import *
from features.shopping_cart.spiels import SPIELS
from features.payments.dragonpay.dragonpay import *
from features.payments import resend_pin_code
from features.payments.payment import  get_paypal_expresscheckout_url


from features.shortcode.exceptions import NoSuffixException
import features.logging as sms_api_logger
from utils.mobile_formatting_util import InvalidMobileFormatException, \
    MobileNotSmartException

from features.paypal import paypal_main

#import paymaya / credit card features
from features.paymaya import paymaya_main
from urllib2 import Request, urlopen
from pprint import pprint
from models.shopping_cached_cart import ShoppingCachedCart as CachedCart

#import redis
from models import redisconn

PLAN_NAME = 'plan_qty%s'

@route(['/cart', '/cart/'])
class PurchasePackageHandler(BaseHandlerSession):
    '''
        @description:
            - renders purchase_package.html
            where users can view available
            packages and add them to cart
    '''

    @authenticated
    @asynchronous
    def get(self):
        account_id = self.get_current_user().account_id

        packages_list = []
        cart_items_count = 0

        try:
            packages_list = get_packages()
            rates = Checkout.get_carrier_charging()

        except:
            print 'unable to get packages'

        try:

            # gets how many items in user cart (for notif purpose)
            cart_items_count = get_cart_items_count(account_id)

            # returns all packages in table

        except NoSuffixException, e:
            print 'exception raised while loading cart data', e

            #self.redirect('/shortcode')
        except Exception, e:
            print e

        # get notifications
        generic_notification = None
        notification_type = self.get_argument('notif-type', None)
        if notification_type ==  'cancel-smart-payment':
            generic_notification = 'Your transaction has been cancelled. To purchase, please select a package.'
        elif notification_type ==  'checkout-expired':
            generic_notification = 'Session expired, please purchase again'
        elif notification_type ==  'code-expired':
            generic_notification = 'Your PIN code has expired. The code is only valid for 30 minutes. To purchase, please select a package.'
        if notification_type ==  'dragonpay-token-failed':
            generic_notification = 'DragonPay is not available at the moment. Please try again in a few minutes or choose another payment method'

        self.render('purchase_package.html',
                    packages_list=packages_list,
                    cart_items_count=cart_items_count,
                    rates=rates,
                    generic_notification=generic_notification)


@route(['/cart/view', '/cart/view/'])
class CartViewHandler(BaseHandlerSession):
    '''
        @description:
            - allows the user to view the
            items he/she added to cart
    '''

    @authenticated
    @asynchronous
    def post(self):
        self.get()

    @authenticated
    @asynchronous
    def get(self):


        current_user = self.get_current_user()
        account_id = current_user.account_id
        balance_notif_enabled = current_user.balance_notif_enabled
        current_balance = current_user.balance
        balance_threshold = current_user.balance_notif_threshold
        display_threshold_warning = False

        #paymaya error message
        paymaya_error_key = "%s" % self.get_current_user().account_id + "-paymaya-error"
        paymaya_error_message = redisconn.get(paymaya_error_key) or None
        redisconn.delete(paymaya_error_key)

        cart_items = None
        error_message = None

        threshold_warning_message = ''

        threshold_warning_message = 'We\'ve noticed that your current balance together with the credits you are purchasing will still be below your defined threshold of (P%s). Please note that you will continue to receive low balance notifications via email until your balance is above the defined threshold.'% current_user.balance_notif_threshold

        try:
            cart_items = get_cart_items(account_id)

            if current_user.balance and balance_notif_enabled and cart_items:

                total = 0
                for citem in cart_items:
                    total+=float(citem['amount'])

                below_threshold = True if balance_threshold > ( float(current_user.balance)+float(total)  ) else False

                if below_threshold :
                    display_threshold_warning = True


        except CartEmptyException, e:
            error_message = SPIELS['terror1']
            self.redirect('/cart/empty')
            return
        except NoSuffixException, e:
            # self.redirect('/shortcode')
            print e

        self.render('shopping_cart.html',
            error_message=error_message,
            paymaya_error_message=paymaya_error_message,
            cart_items=cart_items, dumps=dumps,
            current_balance=current_balance,
            balance_threshold=balance_threshold,
            display_threshold_warning=display_threshold_warning,
            threshold_warning_message=threshold_warning_message)


@route(['/cart/add', '/cart/add/'])
class CartAddHandler(BaseHandlerSession):
    '''
        @description:
            - allows user to add to his/her cart
    '''

    @authenticated
    @asynchronous
    def post(self):

        account_id = self.get_current_user().account_id

        new_item = {
            'id': self.get_argument('plan_id'),
            'quantity': self.get_argument('quantity')
            # 'plan_code': self.get_argument('plan_code'),
            # 'amount': self.get_argument('amount'),
            # 'credits': self.get_argument('credits'),
            # 'days_valid': self.get_argument('days_valid')
            # 'days_valid': 3
        }

        cart_count = len(add_update_cart(account_id, new_item))

        response = {
            'count' : str(cart_count),
            'message' : SPIELS['tsuccess1'] % self.get_argument('plan_code')
        }

        self.finish(dumps(response))

@route(['/cart/wipeout', '/cart/wipeout/'])
class CartAddHandler(BaseHandlerSession):

    # @authenticated
    # @asynchronous
    # def get(self):
        # self.post()
        # self.finish()

    @authenticated
    @asynchronous
    def get(self):
        account_id = self.get_current_user().account_id
        wipe_out_cached_cart(account_id)
        self.redirect('/cart/empty')

@route(['/cart/remove/([\d]+)', '/cart/remove/([\d]+)/'])
class CartAddHandler(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self, plan_id):
        account_id = self.get_current_user().account_id
        delete_from_cart(account_id, plan_id)
        self.redirect('/cart/view')


@route(['/cart/checkout', '/cart/checkout/'])
class CartCheckoutHandler(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self):
        self.post()

    @authenticated
    @asynchronous
    def post(self):

        current_user = self.current_user

        account_id = self.get_current_user().account_id
        plan_quantities = self.get_argument('plan_quantities')
        plan_quantities = plan_quantities.split('|,') or []

        """
        # retrieves all the updated quantities plans in cart
        # based on user inputs from the form

        # ! now handled by JS --> using ajax call !

        cart_ids = self.get_argument('cart_ids') or []
        cart_ids = eval(cart_ids)
        plan_quantities = []
        cart_items = None
        error_message = None

        i = 0
        while i < (len(cart_ids)):
            plan_quantity = PLAN_NAME % str(cart_ids[i])
            plan = {
                'id' : cart_ids[i],
                'quantity': self.get_argument(plan_quantity)
            }
            plan_quantities.append(plan)
            i += 1

        try:
            cart_items = checkout_cart(account_id, plan_quantities)

        except Exception, e:
            error_message = e
        """

        response = {
            'cart_items': [],
            'total_cost': 0,
            'enable_dragon_pay' : False,
            'enable_paypal' : False
        }

        try:
            response['cart_items'] = checkout_cart(account_id, plan_quantities)
            response['total_cost'] = compute_total_amount(response['cart_items'])

            # determine if dragon pay will be allowed as a payment option
            response['enable_dragon_pay'] = is_allowed_for_amount( response['total_cost'] )

            # determine if paypal will be allowed

            response['has_pending_paypal_purchase'] = paypal_main.has_pending_paypal_purchase( account_id=current_user.account_id )

            response['current_paypal_purchases'] = paypal_main.get_total_paypal_purchases_for_current_month( account_id=current_user.account_id )
            response['current_paypal_purchases_formatted'] = format( float(response['current_paypal_purchases']), ',.0f')

            response['allowed_total_paypal_purchases'] = paypal_main.is_within_allowed_paypal_purchases( account_id=current_user.account_id, amount=response['total_cost'], current_purchases=response['current_paypal_purchases'] )

            response['max_paypal_purchases'] = paypal_main.allowed_purchases_per_month
            response['max_paypal_purchases_formatted'] = format( float(response['max_paypal_purchases']) , ',.0f')

            response['enable_paypal'] = paypal_main.is_allowed_for_amount( response['total_cost'] )

            #check if paymaya / credit card option payment is allowed
            response['enable_paymaya'] = paymaya_main.is_allowed_for_amount( response['total_cost'] )


        except Exception, e:
            print e

        self.finish(dumps(response))
        # self.render('checkout.html',
            # error_message=error_message,
            # cart_items=cart_items)

@route(['/cart/payment', '/cart/payment/'])
class CartPaymentSmartHandler(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self):
        self.post()

    @authenticated
    @asynchronous
    def post(self):


        logger = sms_api_logger.GeneralLogger()
        logger.info('received shopping cart payment request')

        '''
            allowed payment_type: [
                smart, credit_card, seven_eleven,
                dragonplay, globe_cashformat( 300000, ',.2f')
            ]
        '''

        account_id = self.get_current_user().account_id
        try:
            cart_items_count = get_cart_items_count(account_id)
            if cart_items_count == 0:
                self.redirect('/cart')

        except NoSuffixException, e:
            self.redirect('/shortcode')
        except Exception, e:
            print e

        payment_type = self.get_argument('radio')
        error_message = None

        if payment_type == 'SMART':

            logger.info('payment type is via SMART PAYMENT GATEWAY')

            self.render('payment_smart_mobile.html',
                error_message=error_message,
                mobile=None, checkout_id=None,
                is_pincode_page=False,
                perror_message=None)
            return

        elif payment_type == 'DRAGONPAY':

            logger.info('payment type is via DRAGON PAY')

            try:

                # saves neccessary data to DB and cache

                amount = compute_total_amount(get_cart_items(
                    self.get_current_user().account_id))

                checkout_id = process_dragonpay_checkout(
                    account_id=self.get_current_user().account_id,
                    amount=amount)

                # saves txn_id and unique chikka api token to
                # identify dragonpay in future transactions
                ctoken_id = save_dragonpay_data(checkout_id=checkout_id)

                # obtains dragon pay token id;
                # ctoken_id will be passed as param1 to soapcall
                # which will be used for extra authentication in future

                dragonpay_token = get_dragonpay_token(
                    account_id=self.get_current_user().account_id,
                    checkout_id=checkout_id, email=self.get_current_user().email,
                    amount=amount, param1=ctoken_id)

                logger.info('acquired dragonpay token', dragonpay_token)

                self.redirect(self.settings['dragonapi_url'] % dragonpay_token)

            except Exception, e:
                logger.error('exception raised while processing dragon pay payment', str(e))
                import traceback
                print traceback.format_exc()
                self.redirect('/cart?notif-type=dragonpay-token-failed')

            return

        elif payment_type == 'PAYPAL':

            amount = compute_total_amount(get_cart_items(
                    self.get_current_user().account_id))
            logger.info('payment type is via PAYPAL', {'amount':amount})
            try:

                checkout_id = process_paypal_checkout(account_id, amount)
            except Exception, e:
                logger.error('exception rasied while checkout via paypal: %s' %e)
                checkout_id = None

            if checkout_id :
                logger.info('checkout id %s generated' % checkout_id)
                try :

                    url = get_paypal_expresscheckout_url( checkout_id=checkout_id )
                    if url:
                        logger.info('redirecting user to: %s' % url)
                        self.redirect( url )
                        return
                    else:
                        raise Exception('no URL generated')


                except Exception, e:
                    logger.error( 'unable to get paypal express checkout. try again: %s' % e, {'checkout_id': checkout_id }  )
                self.redirect('/cart')

            else:
                logger.error('no checkout record created. redirecting to /cart')
                self.redirect('/cart')

        elif payment_type == 'PAYMAYA':
            amount = compute_total_amount( get_cart_items( self.get_current_user().account_id) )
            logger.info('payment type is via PAYMAYA', {'amount':amount})


            #set error message to redis
            paymaya_error_key = "%s" % self.get_current_user().account_id + "-paymaya-error"
            formatted_limit = "{:,}".format( paymaya_main.paymaya_amount_limit )
            ### check if current checkout is more than set LIMIT ###
            if amount >= paymaya_main.paymaya_amount_limit :
                redisconn.set(paymaya_error_key, "The monthly limit for purchases using VISA/Mastercard via PayMaya is %s. Kindly purchase a smaller amount." % formatted_limit)
                self.redirect('/cart/view')

            ### check monthly limit if it exceeds config settings ###
            verify_limit = paymaya_main.verify_monthly_limit (self.get_current_user().account_id, amount)
            print "#####verify_limit#####"
            print verify_limit

            if verify_limit['status']:
                paymaya_error_message = "The monthly limit for purchases using VISA/Mastercard via PayMaya is {}. You have already purchased {}. Kindly select a smaller amount.".format( formatted_limit, verify_limit['total_for_the_month'])
                redisconn.set(paymaya_error_key, paymaya_error_message)
                self.redirect('/cart/view')

            try:

                checkout_id = process_paymaya_checkout(account_id, amount)
            except Exception, e:
                logger.error('exception rasied while checkout via paymaya: %s' %e)
                checkout_id = None

            if checkout_id :

                remote_ip = self.request.remote_ip or ""

                logger.info('checkout id %s generated' % checkout_id)
                try :

                    paymaya_checkout_url = paymaya_main.get_paymaya_checkout_url()

                    #build headers
                    paymaya_request_headers = paymaya_main.get_request_headers()

                    #build params
                    paymaya_cart_items = get_cart_items(self.get_current_user().account_id)
                    paymaya_request_params = paymaya_main.get_request_params( self.get_current_user(), paymaya_cart_items, remote_ip, checkout_id)

                    print paymaya_request_params
                    request = Request(paymaya_checkout_url, data=paymaya_request_params, headers=paymaya_request_headers)

                    response_body = loads(urlopen(request).read())
                    #save to paymaya_checkout table

                    paymaya_main.save_paymaya_checkout( checkout_id, response_body['checkoutId'], 'CREATED', 'PENDING' )
                    self.redirect( response_body['redirectUrl'] )

                    #wipeout cart cache
                    CachedCart.wipe_out_cart(account_id)
                    self.finish()

                except Exception, e:
                    logger.error( 'unable to get paymaya express checkout. try again: %s' % e, {'checkout_id': checkout_id }  )
                self.redirect('/cart')

            else:
                logger.error('no checkout record created. redirecting to /cart')
                self.redirect('/cart')
        else:
            self.write('Payment type not available YET.')
            self.finish()

@route(['/cart/payment/smart/mobile', '/cart/payment/smart/mobile/'])
class CartPaymentSmartPincodeHandler(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self):
        self.post()

    @authenticated
    @asynchronous
    def post(self):

        account_id = self.get_current_user().account_id
        mobile = self.get_argument('mobile', '')
        error_message = None
        is_pincode_page = False
        checkout_id = None

        try:
            cart_items_count = get_cart_items_count(account_id)
            if cart_items_count == 0:
                self.redirect('/cart')

        except NoSuffixException, e:
            self.redirect('/shortcode')
        except Exception, e:
            print e

        try:
            # amount is recomputed. this protects us
            # from hackers which injects their own amount param
            amount = compute_total_amount(get_cart_items(account_id))
            checkout_id = process_smart_payment_authentication( account_id, mobile, amount)

        except InvalidMobileFormatException, e:
            print e
            error_message = SPIELS['terror2']
        except MobileNotSmartException, e:
            print e
            error_message = SPIELS['terror5']
        except Exception, e:
            print e
        else:
            is_pincode_page = True

            # if successful is correct, redirect to enter code page
            # redirect
            self.redirect('/cart/payment/smart/enter-pincode?cid=%s'%checkout_id)
            return


            # self.render('payment_smart_mobile.html',
                # error_message=error_message,
                # mobile=mobile, amount=amount,
                # checkout_id=checkout_id)

        if error_message:
            self.render('payment_smart_mobile.html',
            error_message=error_message,
            # amount=amount,
            mobile=mobile, checkout_id=checkout_id,
            is_pincode_page=is_pincode_page,
            perror_message=None)


@route(['/cart/payment/smart/pincode', '/cart/payment/smart/pincode/'])
class CartPaymentSmartPincodeHandler(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self):
        self.post()

    @authenticated
    @asynchronous
    def post(self):

        account_id = self.get_current_user().account_id
        pincode = self.get_argument('pincode', '') # should not be none TO DO JS
        checkout_id = self.get_argument('checkout_id')
        #mobile = self.get_argument('mobile') # should be deprecated.
        perror_message = None

        try:
            checkout_id = int(checkout_id)
            checkout_object = SmartPaymentGatewayCheckout.get( checkout_id = checkout_id )

            process_smart_payment_verification( account_id, pincode, checkout_id)

        except CartEmptyException, e:
            perror_message = SPIELS['terror1']
            self.redirect('/cart/empty')
        except IncorrectPincodeException, e:
            perror_message = SPIELS['terror3']
        except ExpiredPincodeException, e:
            # redirect to packages with error messages
            self.redirect('/cart?notif-type=code-expired')
            return
            perror_message = SPIELS['terror4']
        except CheckoutQueuePushException, e:
            perror_message = SPIELS['terror6']
        # except MaxCodeRetriesException, e:
            # perror_message = SPIELS['terror5']

        except Exception, e:
            self.redirect('/cart')

        else:

            # updates current account object
            # for rendering purposes
            self.current_user.package = 'PAID'

            # redirect to dashboard
            self.redirect('/dashboard?notif-type=smart-payment-confirmed'   )
            return

        if perror_message:
            self.render('page-smart-payment-pin.html',
                error_message=None,
                perror_message=perror_message,
                # amount=amount,
                checkout_id=checkout_id,
                is_pincode_page=True,
                mobile = checkout_object.phone,

                )
            return

@route( '/cart/payment/smart/enter-pincode'  )
class SmartPaymentEnterCodeResend( BaseHandlerSession ):

    @authenticated
    @asynchronous
    def get(self):

        logger = sms_api_logger.GeneralLogger()


        checkout_id = self.get_argument('cid', None)

        current_user = self.current_user

        try :
            logger.info('attempting to pay via smart payment', {'current_account_id':current_user.account_id, 'checkout_id' :checkout_id })

            checkout_id = int(checkout_id)
            checkout_object = get_checkout_for_enter_code( account_id=current_user.account_id, checkout_id=checkout_id )


        except CheckoutExpiredError, e :
            logger.error('enter pin code screen: EXPIRED ; %s' %e , {'current_account_id':current_user.account_id, 'checkout_id' :checkout_id })
            self.redirect('/cart?notif-type=code-expired')
        except Exception ,e :
            logger.error('enter pin code screen: %s' %e , {'current_account_id':current_user.account_id, 'checkout_id' :checkout_id })
            self.redirect('/cart')

        else:
            self.render('page-smart-payment-pin.html', checkout_id=checkout_id,
                        perror_message=None, mobile=checkout_object.phone )

    @authenticated
    @asynchronous
    def post(self):
        pass


@route(['/cart/empty', '/cart/empty/'])
class EmptyCartRenderer(BaseHandlerSession):

    @asynchronous
    @authenticated
    def get(self):
        self.render('cart_empty.html')


@route('/cart/payment/ajax/resend-sms')
class ResendSMSCodeAjaxHandler( BaseHandlerSession ):

    @asynchronous
    @authenticated
    def get(self):

        logger = sms_api_logger.GeneralLogger()
        checkout_id = self.get_argument( 'checkout_id', None )
        response = {'result' : False, 'error_message':''}

        default_log_data = {'checkout_id' : checkout_id, 'current_account_id' : self.current_user.account_id }

        try :
            logger.info( 'requesting resend sms', default_log_data )
            resend_pin_code.resend_sms( checkout_id=checkout_id )
            response['result'] = True
            response['success_message'] = "A PIN code has been sent. You may request to resend PIN code up to 3x per transaction only. Your PIN is valid for 30 minutes."
            logger.info( 'resend sms request success', default_log_data )
        except resend_pin_code.MaxResendReachedError ,e:
            logger.error( 'max resends reached' , default_log_data )
            response['error_message'] = 'You have reached the maximum number of PIN code requests per transaction. Please wait for your PIN code to arrive.'


        except resend_pin_code.ResendTimeLimitReached, e :
            logger.error( 'resend time limit reached' , default_log_data )
            response['error_message'] = 'Request to resend PIN code for this transaction has expired. Please take note that PIN validity is 30 mins. If you haven\'t received your PIN'
        except Exception, e :
            logger.error( 'unexpected error: %s' % e , default_log_data )
            response['result'] = False



        self.write( dumps(response) )
        self.finish()

@route('/payments/paymaya/success')
class PaymayaCheckoutSuccessHandler( BaseHandlerSession ):

    @authenticated
    @asynchronous
    def get(self):

        logger = sms_api_logger.GeneralLogger()
        checkout_id = self.get_argument('checkout_id')

        #check if transaction is already successfull then redirect to dashboard
        if paymaya_main.is_already_successful( checkout_id ) :
            self.redirect("/dashboard");

        paymaya_checkout_details = paymaya_main.get_payamaya_checkout_details( checkout_id )

        #call Paymaya checkout information
        if paymaya_checkout_details['paymaya_checkout_id']:
            try :

                paymaya_checkout_url = paymaya_main.get_paymaya_checkout_url() + "/" + paymaya_checkout_details['paymaya_checkout_id']

                #build headers
                paymaya_request_headers = paymaya_main.get_request_headers('secret_key')

                # #build params
                request = Request(paymaya_checkout_url, headers=paymaya_request_headers)

                response_body = loads(urlopen(request).read())

                #update checkout details
                update_params = {
                    'receipt_number' : response_body['receiptNumber'] or  "",
                    'transaction_reference_number' : response_body['transactionReferenceNumber'] or "",
                    'status' : response_body['status'],
                    'payment_status' :  response_body['paymentStatus']
                }

                paymaya_main.update_paymaya_checkout_details( checkout_id, update_params )
                if response_body['status'] == "COMPLETED" and response_body['paymentStatus'] == "PAYMENT_SUCCESS" :
                    paymaya_main.on_payment_success( checkout_id, self.get_current_user().account_id )
                self.redirect("/dashboard")

            except Exception, e:
                logger.error( 'unable to get paymaya express checkout. try again: %s' % e, {'checkout_id': checkout_id }  )

        self.finish()


@route('/payments/paymaya/failed')
class PaymayaCheckoutSuccessHandler( BaseHandlerSession ):

    @authenticated
    @asynchronous
    def get(self):

        logger = sms_api_logger.GeneralLogger()
        checkout_id = self.get_argument('checkout_id')


        paymaya_checkout_details = paymaya_main.get_payamaya_checkout_details( checkout_id )

        print paymaya_checkout_details

        #call Paymaya checkout information
        if paymaya_checkout_details['paymaya_checkout_id']:
            try :

                paymaya_checkout_url = paymaya_main.get_paymaya_checkout_url() + "/" + paymaya_checkout_details['paymaya_checkout_id']

                #build headers
                paymaya_request_headers = paymaya_main.get_request_headers('secret_key')

                # #build params
                request = Request(paymaya_checkout_url, headers=paymaya_request_headers)

                response_body = loads(urlopen(request).read())

                #update checkout details
                update_params = {
                    'receipt_number' : response_body['receiptNumber'] or  "",
                    'transaction_reference_number' : response_body['transactionReferenceNumber'] or "",
                    'status' : response_body['status'],
                    'payment_status' :  response_body['paymentStatus']
                }

                paymaya_main.update_paymaya_checkout_details( checkout_id, update_params )
                paymaya_main.on_payment_failed( checkout_id, self.get_current_user().account_id )

                self.redirect("/dashboard")

            except Exception, e:
                logger.error( 'unable to get paymaya express checkout. try again: %s' % e, {'checkout_id': checkout_id }  )

        self.finish()

@route('/paymaya/webhooks/success')
class CheckoutHookSuccessHandler (BaseHandlerSession):

    def post(self):
        logger = sms_api_logger.GeneralLogger()
        data = json.loads(self.request.body)
        # logger.info('start :: CheckoutHookSuccessHandler :: request_body =' % data)
        print '=============='
        print type(data)
        print '=============='

        params = {
            'receipt_number' : data['receiptNumber'] or  "",
            'transaction_reference_number' : data['transactionReferenceNumber'] or "",
            'status' : data['status'] or "",
            'payment_status' :  data['paymentStatus'] or ""
        }

        #get checkout_id in paymaya_checkout
        checkout_id = paymaya_main.get_checkout_id(data['id']);
        _checkout_id = checkout_id['checkout_id']
        params.update({'checkout_id': _checkout_id})
        print _checkout_id

        #update paymaya_checkout to success
        paymaya_main.update_paymaya_checkout_details(_checkout_id, params)

        if data['status'] == "COMPLETED" and data['paymentStatus'] == "PAYMENT_SUCCESS" :
            print "update purchase history"

            #get account_id in purchase_history
            account_id = paymaya_main.get_account_id_by_purchase_history(_checkout_id)
            params.update({'id': account_id})

            #update purchase history to success
            paymaya_main.on_payment_webhook_success(_checkout_id, account_id)
        # logger.info('end :: CheckoutHookSuccessHandler')
        print "end of webhooks success"
        self.write(json.dumps(params))
        self.finish()

@route('/paymaya/webhooks/failed')
class CheckoutHookFailedHandler (BaseHandlerSession):
    def post(self):
        logger = sms_api_logger.GeneralLogger()
        data = json.loads(self.request.body)
        # logger.info('start :: CheckoutHookFailedHandler :: request_body =' % data)
        print '=============='
        print type(data)
        print '=============='
        params = {
            'receipt_number' : data['receiptNumber'] or  "",
            'transaction_reference_number' : data['transactionReferenceNumber'] or "",
            'status' : data['status'] or "",
            'payment_status' :  data['paymentStatus'] or ""
        }

        #get checkout_id in paymaya_checkout
        checkout_id = paymaya_main.get_checkout_id(data['id']);
        _checkout_id = checkout_id['checkout_id']
        params.update({'checkout_id': _checkout_id})
        print _checkout_id

        #update paymaya_checkout to failed
        paymaya_main.update_paymaya_checkout_details(_checkout_id, params)

        #get account_id in purchase_history
        account_id = paymaya_main.get_account_id_by_purchase_history(_checkout_id)
        params.update({'id': account_id})

        #update purchase history to failed
        paymaya_main.on_payment_webhook_failed(_checkout_id, account_id)

        # logger.info('end :: CheckoutHookFailedHandler')
        self.write(json.dumps(params))
        self.finish()
