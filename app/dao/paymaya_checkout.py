'''
@author: sarz - makmakulet ;)
this DAO will be in charge of transacting with the application's databse
for storring/updating Paymaya Checkouts tokens

requires some sort of sql util
'''




# use paymaya dao interface
from features.paymaya.dao_interface import PaymayaDAOInterface
from models.checkout import *
import utils.add_sms_credits as credit_tool

class PaymayaCheckoutDao( object, PaymayaDAOInterface ):

    _table='paymaya_checkout'

    def __init__(self, sql_util):


        self.sql_util = sql_util

        pass

    def create (self, checkout_id, paymaya_checkout_id, status, payment_status) :
      params = {'checkout_id' : checkout_id,
        'paymaya_checkout_id': paymaya_checkout_id,
        'status': status,
        'payment_status': payment_status,
      }
      result = self.sql_util.execute_insert( table_name=self._table, params=params)

    def update (self, checkout_id, update_params) :
      condition = {'checkout_id' : checkout_id}
      try:
          result = self.sql_util.execute_update( table_name=self._table, params=update_params, conditions=condition)
          if result:
              return True
          else:
              return False

      except Exception, e:
          raise PaymayaDaoException('could not update record: %s' % e)


    def get_by_checkout_id (self, checkout_id) :
      criteria = { 'checkout_id' : checkout_id }
      table_cols = ['id', 'checkout_id', 'paymaya_checkout_id', 'status', 'payment_status', 'date_created']

      record = self.sql_util.execute_select(
          table_name=self._table,
          conditions=criteria,
          operator='AND', table_cols=table_cols,
          fetchall=False)

      return record

    # get checkout_id for payamaya webhooks update success/failed
    def get_paymaya_checkout_id(self, checkout_id):
        limit = 1
        criteria = { 'paymaya_checkout_id' : checkout_id }
        table_cols = ['checkout_id']
        record = self.sql_util.execute_select(
            table_name=self._table,
            conditions=criteria,
            operator='AND', table_cols=table_cols,
            limit=limit, fetchall=False)

        return record


    def update_checkout_status (self, checkout_id, status = 'SUCCESS') :

        criteria = {'id' : checkout_id}
        update_params = {'status': status}

        print "##########update_checkout_status##########"
        print criteria
        print update_params
        print "##########update_checkout_status##########"
        try:
          result = self.sql_util.execute_update( table_name='checkout', params=update_params, conditions=criteria)

        except Exception, e:
          raise PaymayaDaoException('could not update record: %s' % e)



    def update_account_type (self, account_id, package = 'PAID') :

        criteria = {'id' : account_id}
        update_params = {'package': package}
        try:
          result = self.sql_util.execute_update( table_name='accounts', params=update_params, conditions=criteria)

        except Exception, e:
          raise PaymayaDaoException('could not update record: %s' % e)



    def get_credit_transaction_id (self, suffix, amount) :

        charging = Checkout.get_carrier_charging()

        return  credit_tool.add_credits( suffix, amount, charging )


class PaymayaDaoException( Exception ):
    pass
