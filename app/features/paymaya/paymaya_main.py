'''
contains general profedures for paymaya payment system


@author: sarz - makmakulet ;)

'''
import base64
from ujson import loads, dumps
from . import paymaya_settings, sql_util, all_configs
from pprint import pprint
from features.shopping_cart.shopping_cart import compute_total_amount
from dao.paymaya_checkout import *
from features.payments.checkout import *
from models.account import *
from features.payments.notification import *
from dao.purchase_history_mysql import *
from datetime import datetime

from models.checkout import Checkout
from models.account import Account
paymaya_min_amount_peso = 500
paymaya_amount_limit = 300000


################## AMOUNT VERIFICATION ##################
def is_allowed_for_amount( amount ):

    is_allowed = False
    try:
        if int(amount) >= paymaya_min_amount_peso:
            is_allowed = True
    except Exception, e:
        is_allowed = False

    return is_allowed

################## CHECKOUT URL ##################
def get_paymaya_checkout_url ():
    return "/".join([paymaya_settings['api_base_url'], paymaya_settings['endpoint'], paymaya_settings['version'], paymaya_settings['route']])

################## REQUEST HEADERS ##################
def get_request_headers (_type = 'public_key'):

    base64_encoded_key = base64.b64encode( paymaya_settings[_type] + ":")

    return {
      "Content-Type": "application/json",
      "Authorization": "Basic " + base64_encoded_key
    }

################## REQUEST PARAMS / BODY ##################
def get_request_params ( current_user, cart_items, remote_ip, checkout_id ):
    # pprint(vars(current_user))
    total_amount = compute_total_amount( cart_items )

    items = []
    for item in cart_items:
      total_item_value = float(item['amount']) * int(item['quantity'])
      items.append({
        "name" : item['plan_code'],
        "code": item['id'],
        "code": item['id'],
        "description": "Package Plan",
        "quantity": "%s" % item['quantity'],
        "amount": {
          "value": "{:.2f}".format( float(item['amount']))
        },
        "totalAmount": {
          "value": "{0:.2f}".format( float(total_item_value) )
        }
      })

    params =   {
      "totalAmount": {
        "currency": "PHP",
        "value": "{:.2f}".format(total_amount),
      },
      "buyer": {
        "firstName": "%s" % current_user._first_name or current_user.account_id,
        "lastName": "%s" % current_user._last_name or current_user.email,
        "contact": {
          "phone": "%s" % current_user.test_min,
          "email": current_user.email
        },
        "ipAddress": remote_ip
      },
      "items": items,
      "redirectUrl": {
        "cancel": all_configs['website_base_url'] + paymaya_settings['cancelled_url'] + "?checkout_id=%s" % checkout_id,
        "failure": all_configs['website_base_url'] + paymaya_settings['failed_url'] + "?checkout_id=%s" % checkout_id,
        "success": all_configs['website_base_url'] + paymaya_settings['success_url'] + "?checkout_id=%s" % checkout_id
      },
      "requestReferenceNumber": "%s" % checkout_id,
      "metadata": {}
    }

    return dumps(params)

################## STORE TO PAYMAYA CHECKOUT  ##################
def save_paymaya_checkout (checkout_id, paymaya_checkout_id, status, payment_status):
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)
  return paymaya_checkout_dao.create( checkout_id, paymaya_checkout_id, status, payment_status )

def get_payamaya_checkout_details (checkout_id):
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)
  return paymaya_checkout_dao.get_by_checkout_id( str(checkout_id) )

#get checkout_id in paymaya checkout that used for webhooks success/failed
def get_checkout_id_by_paymaya_checkout (checkout_id):
    paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)
    return  paymaya_checkout_dao.get_paymaya_checkout_id( str(checkout_id) )

def update_paymaya_checkout_details (checkout_id, update_params):
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)
  return paymaya_checkout_dao.update( str(checkout_id), update_params )

def is_already_successful (checkout_id):
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)
  checkout_object = paymaya_checkout_dao.get_by_checkout_id(checkout_id)

  if checkout_object['status'] == 'COMPLETED' and checkout_object['payment_status'] == 'PAYMENT_SUCCESS':
    return True
  else :
    return False


def verify_monthly_limit (account_id, amount) :

  total_for_the_month = get_total_amount_for_the_month (account_id)

  print "####### total_for_the_month #########"
  print total_for_the_month

  combined_amount = (float(total_for_the_month) + float(amount))

  if combined_amount >= paymaya_amount_limit :
    return {"status": True, "total_for_the_month": total_for_the_month}
  else :
    return {"status": False, "total_for_the_month": total_for_the_month}


def get_total_amount_for_the_month (account_id):

  purchase_history_mysql = PurchaseHistoryMysqlDAO(sql_util)

  current_date = datetime.now()

  return  purchase_history_mysql._get_total_purchase_per_type_per_month (account_id, 'PAYMAYA', current_date)


def on_payment_success (checkout_id, account_id):

  #get checkout OBJECT
  checkout_object = Checkout.get( checkout_id=checkout_id)
  print "======checkout_object====="
  pprint (checkout_object)
  print "======checkout_object====="

  #get account OBJECT
  account_object = Account.get( account_id=account_id )
  print "======account_object====="
  pprint (account_object)
  print "======account_object====="

  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)

  ###### STEP 1 ######
  #update checkout status
  paymaya_checkout_dao.update_checkout_status( checkout_id )

  ###### STEP 2 ######
  #update account type to 'PAID'
  if account_object.package_type != Account.PACKAGE_PAID :
    paymaya_checkout_dao.update_account_type( account_id )

  ###### STEP 3 ######
  #add credits to sms api
  credit_trans_id = paymaya_checkout_dao.get_credit_transaction_id( account_object.suffix, checkout_object.amount)

  if credit_trans_id :
    checkout_object.credit_trans_id = credit_trans_id
    # refresh balance in the object (auto clears flags if needed)
    account_object.refresh_credit_balance()

  ###### STEP 4 ######
  #update purchase history
  checkout_object.status = Checkout.STATUS_SUCCESS
  checkout_object.write_to_purchase_history()

  ###### STEP 5 ######
  payment_notif_tool.notify_payment_successful( account_object, checkout_object )

def get_account_id_by_checkout (checkout_id):
    checkout_object = Checkout.get( checkout_id=checkout_id)
    return checkout_object.account_id

def on_payment_failed (checkout_id, account_id):

  #get checkout OBJECT
  checkout_object = Checkout.get( checkout_id=checkout_id)

  #get account OBJECT
  account_object = Account.get( account_id=account_id )

  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)

  #update checkout status as failed
  paymaya_checkout_dao.update_checkout_status( checkout_id, 'FAILURE' )

  #update purchase history
  checkout_object.status = Checkout.STATUS_FAILURE
  checkout_object.write_to_purchase_history()

def on_payment_webhook_success (checkout_id, account_id):

  #get checkout object in checkout db
  checkout_object = Checkout.get( checkout_id=checkout_id)
  print checkout_object

  #get account object in account db
  account_object = Account.get( account_id=account_id )
  print account_object

  #paymaya_checkout db initilize
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)

  ###### STEP 1 ######
  #update checkout status
  paymaya_checkout_dao.update_checkout_status( checkout_id )

  ###### STEP 2 ######
  #update account type to 'PAID'
  if account_object.package_type != Account.PACKAGE_PAID :
    paymaya_checkout_dao.update_account_type( account_id )

  ###### STEP 3 ######
  #add credits to sms api
  credit_trans_id = paymaya_checkout_dao.get_credit_transaction_id( account_object.suffix, checkout_object.amount)

  if credit_trans_id :
    checkout_object.credit_trans_id = credit_trans_id
    # refresh balance in the object (auto clears flags if needed)
    account_object.refresh_credit_balance()

  ###### STEP 4 ######
  #update purchase history
  checkout_object.status = Checkout.STATUS_SUCCESS
  checkout_object.write_to_purchase_history()

  ###### STEP 5 ######
  payment_notif_tool.notify_payment_successful( account_object, checkout_object )


def on_payment_webhook_failed (checkout_id, account_id):

  #get checkout object in checkout db
  checkout_object = Checkout.get( checkout_id=checkout_id)

  #get account object in account db
  account_object = Account.get( account_id=account_id )

  #paymaya_checkout db initilize
  paymaya_checkout_dao = PaymayaCheckoutDao(sql_util)

  #update checkout status as failed
  paymaya_checkout_dao.update_checkout_status( checkout_id, 'FAILURE' )

  #update purchase history
  checkout_object.status = Checkout.STATUS_FAILURE
  checkout_object.write_to_purchase_history()
