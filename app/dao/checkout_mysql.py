from models.checkout import *
from datetime import datetime

class CheckoutMysqlDAO( object ):

    sql_util = None


    default_fields = ['id', 'account_id', 'suffix', 'phone', 'code', 'amount', 'date_expiry', 'mode_of_payment',
                  'status', 'retry_ctr', 'date_created', 'date_updated', 'expired', 'remarks']


    def __init__(self, sql_util):


        self.sql_util = sql_util

        pass


    def mark_paid_success(self, checkout_id):
        '''
        marks the checkout record as successfully paid
        set status = 'SUCCESS'

        '''
        coditions = {'id':checkout_id}
        params = { 'status': 'SUCCESS' }

        result = self.__update( conditions=coditions, params=params)
        if result :
            return True
        else:
            # which is unlikely unless record doe not exist
            return False


    def mark_payment_failed(self, checkout_id):
        '''
        marks the checkout record as payment failed
        set status = 'FAILURE'

        '''
        coditions = {'id':checkout_id}
        params = { 'status': 'FAILURE' }

        result = self.__update( conditions=coditions, params=params)
        if result :
            return True
        else:
            # which is unlikely unless record doe not exist
            return False




    def get_for_payment(self, checkout_id ):
        '''
        specific function to get a valid checkout object for payment

        '''

        conditions = { 'id': checkout_id, 'status':'PENDING', 'expired':0 }

        fields = self.default_fields

        record = self.__retrieve( fields, conditions  )

        checkout_object = None

        if record :
            checkout_object = self.__build_checkout_object(record=record)


        return checkout_object



    def increment_sms_resend(self, checkout_id, extend_seconds=None ):
        '''
        increments the sms resend ctr and (optionally) extends the date expiry
        @param checkout_id: the id of the checkout in the database
        @param extend_seconds: integer that describes how long to extend the expiry

        '''

        query = """UPDATE checkout
                    set resend_count=resend_count+1, date_expiry=addtime( date_expiry, sec_to_time(%s) )
                    where id=%s LIMIT 1""" % ( extend_seconds, checkout_id )

        try:
            result = self.sql_util.run_query(query_type='SELECT', query=query)
        except Exception, e:
            print 'oops something went wrong: %s' % e



    def __build_checkout_object(self, record, checkout_type=None):


        if checkout_type:
            checkout_object = checkout_type()
        else:
            checkout_object = Checkout()


        checkout_object.checkout_id = record['id']
        checkout_object.account_id = record['account_id']
        checkout_object.suffix = record['suffix']
        checkout_object.phone = record['phone']
        checkout_object.code = record['code']
        checkout_object.amount = float(record['amount'])

        checkout_object.date_expiry = record['date_expiry']

        checkout_object.mode_of_payment = record['mode_of_payment']

        if record['status'] == 'PENDING' :
            checkout_object.status = Checkout.STATUS_PENDING
        elif record['status'] == 'FAILURE' :
            checkout_object.status = Checkout.STATUS_FAILURE
        elif record['status'] == 'SUCCESS' :
            checkout_object.status = Checkout.STATUS_SUCCESS

        checkout_object.retry_ctr = record['retry_ctr']
        checkout_object.date_created = record['date_created']
        checkout_object.date_updated = datetime.strptime( record['date_updated'] , '%Y-%m-%d %H:%M:%S')


        if record['expired'] == 0 :
            checkout_object.expired = False
        elif record['expired'] == 1 :
            checkout_object.expired = True

        checkout_object.remarks = record['remarks']

        return checkout_object

    def get(self, checkout_id, checkout_type=None ):
        checkout_object = None

        fields = self.default_fields

        conditions = { 'id':checkout_id }

        record = self.__retrieve(fields, conditions)

        if record :
            checkout_object = self.__build_checkout_object(record=record, checkout_type=checkout_type)

        return checkout_object


    def get_smart_payment_checkout(self, checkout_id ):
        '''
        retrieves checkout from database with condition that it is smart mode of payment

        '''

        checkout_object = None
        fields = self.default_fields
        fields.append( 'resend_count' )

        conditions = { 'id':checkout_id, 'mode_of_payment': 'SMART' }

        record = self.__retrieve(fields, conditions)

        if record :
            checkout_object = self.__build_checkout_object(record=record, checkout_type=SmartPaymentGatewayCheckout)
            checkout_object.sms_resend_ctr = record['resend_count']



        return checkout_object


#     def get_checkout_items(self, checkout_id):
#         '''
#         retrieves checkout items from database and formats the list to a readable dictionary
#         '''
#         table_name = 'checkout_items'
#         fields = ['checkout_id', 'plan_code', 'amount', 'quantity']
#
#         conditions = {'checkout_id' : checkout_id }
#
#         formatted_result = None
#
#         print 'dao get checkout items'
#
#         try :
#             result = self.sql_util.execute_select(
#                                                 table_name=table_name,
#                                                 conditions=conditions,
#                                                 table_cols=fields)
#
#             if result:
#                 formatted_result = [{ 'plancode': x['plan_code'], 'amount': x['amount'] , 'qty': x['quantity'] }  for x in result ]
#
#
#         except Exception, e:
#             raise CheckoutReadError('unable to retrieve checkout items: %s' % e )
#
#
#         print 'returning result'
#
#         return formatted_result

    def get_checkout_items(self, checkout_id):
        '''
        @author: vincent agudelo
        retrieves checkout items of a checkout

        '''
        item_records = []

        try:
            checkout_table = 'checkout'
            query = 'SELECT ci.checkout_id, ci.plan_code, ci.quantity, p.plan_description , p.amount from checkout_items ci \
            left join packages p on p.plan_code=ci.plan_code  where checkout_id=%s;' % checkout_id

            db_records = self.sql_util.run_query(query_type='select', query=query, dictionary=True, fetchall=True)

            if db_records :
                item_records = [ { 'plancode': record['plan_code'], 'amount': record['amount'], 'name': record['plan_code'], 'desc' : record['plan_description'],  'qty' : record['quantity'], 'cost' : float(record['amount'])   } for record in  db_records  ]

        except Exception, e:
            item_records = []
            raise CheckoutReadError('could not read checkout record: %s' % e)

        return item_records

    def get_carrier_charging(self):
        '''
        retrieves carrier charging
        '''

        charging = {}
        conditions = {}
        try:
            result = self.sql_util.execute_select(
                                                table_name='carrier_charge',
                                                conditions=conditions,
                                                table_cols=['carrier','amount'],

                                             )
            if result :
                for charge in result :
                    charging[ charge['carrier'] ] = float(charge['amount'])

        except Exception, e :
            raise CarrierChargeReadError( 'unable to read carrier charge: %s' % e )

        return charging


    def __update(self, conditions, params):
        '''
        generic update for record
        '''

        result = None
        try :
            result = self.sql_util.execute_update(
                                                       table_name='checkout',
                                                       params=params,
                                                       conditions=conditions)
        except Exception, e :

            raise CheckoutSaveError( 'unable to save checkout: %s' % e )

        return result

    def __retrieve(self, fields, conditions  ):

        record = None

        try:

            checkout_table = 'checkout'

            record = self.sql_util.execute_select(
                table_name=checkout_table,
                conditions=conditions,
                operator='AND', table_cols=fields,
                fetchall=False)

        except Exception, e:
            raise CheckoutReadError('could not read checkout record: %s' % e)

        return record
