'''
transaction history handler
@author: vincent agudelo


'''

from tornado.web import asynchronous, authenticated
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route

from features.account_management import transaction_history_viewer
from datetime import timedelta, datetime
import ujson as json


@route(['/history/transaction', '/history/transaction/'])
class TransactionHistoryRenderer(BaseHandlerSession):

    @authenticated
    @asynchronous
    def get(self):


        suffix = self.current_user.suffix

        # mo or mt
        which_logs = self.get_argument('in_out', 'in' )


        json_format = self.get_argument('json', False)
        if json_format == 'true' :
            json_format = True

        page_number = self.get_argument('page', 1)
        
        # get filter (used in MT/OUTGOING only)
        smstype_filter = self.get_argument('sms_type', 'all')
        if smstype_filter not in [  'all', 'broadcast', 'reply'  ] :
            smstype_filter = 'all'
        
        try:
            page_number = int(page_number)
        except:
            page_number = 1

        allow_inbox_next = True
        allow_inbox_prev = True
        allow_sent_next = True
        allow_sent_prev = True


        if json_format is True :

            mobile_filter = self.get_argument('mobile_filter', None)

            # get filter if any
            month_filter = self.get_argument('month_filter', None)
            # parse
            m_filter, y_filter = '',''

            if not month_filter:
                month_filter = datetime.now().strftime('%m-%Y')

            if month_filter :

                try :
                    m_filter, y_filter =  month_filter.split('-')
                    m_filter = int(m_filter)%13

                except Exception, e:
                    print 'invalid filter', e

            formatted_trans_record = []

            total_pages = 0

            if which_logs == 'in' :

                try:
                    inbox_info = transaction_history_viewer.get_mo_paginated( self.current_user, page=page_number, m_filter=m_filter, y_filter=y_filter, mobile_filter=mobile_filter )
                    latest_transactions_inbox = inbox_info['records']
                    total_pages = inbox_info['total_pages']


                except Exception, e:
                    print 'exception raised getting inbox', e
                    latest_transactions_inbox = []


            # format fields to be caught by ajax call
                for record in latest_transactions_inbox:
                    
                    t_record = { 'date_time' : "%s - %s" % ( record['date_sent'].strftime('%m/%d/%Y'), record['time_sent']),
                                             'from' : record['from']
                                             
                                              }
                    try:
                        t_record['cost'] = "P%.2f" % float(record['cost'])
                    except Exception, e:
                        t_record['cost'] = record['cost']
                    
                    
                    formatted_trans_record.append( t_record )
            elif which_logs =='out':

                try:
                    outbox_info = transaction_history_viewer.get_mt_paginated( self.current_user, page=page_number, m_filter=m_filter, y_filter=y_filter , mobile_filter=mobile_filter, sms_type_filter=smstype_filter)
                    latest_transactions_inbox = outbox_info['records']

                    total_pages = outbox_info['total_pages']


                except Exception, e :
                    print 'exception raised when getting outbox', e
                    latest_transactions_inbox = []

                # preformat for ajax
                for record in latest_transactions_inbox :

                    t_record = { 'date_time' : "%s - %s" % ( record['date_received'].strftime('%m/%d/%Y'), record['time_received']),
                                                   'to' : record['receiver'],
                                                   'status' : record['status'],
                                                   'message_type' : record['message_type']
                                                    }

                    try:
                        t_record['cost'] = "P%.2f" % float(record['cost'])
                    except Exception, e:
                        t_record['cost'] = record['cost']

                    formatted_trans_record.append( t_record )

            else:
                pass

            self.write( json.dumps( {'transactions': formatted_trans_record, 'total_pages':total_pages } ) )
            self.finish()

        else :


            current_month_display = datetime.now().strftime('%B %Y')

            # default HTML

            #prapare filter

            date_filter_list = []

            months = 6
            current_date = datetime.now()
            year = int(current_date.strftime( '%Y' ))
            month = int( current_date.strftime( '%m' ) )


            current_month = month
            current_year = year

            for x in range(6):
                display_date = datetime( year, month , 1    )

                date_filter_list.append(  {'value':display_date.strftime('%m-%Y'), 'text':display_date.strftime('%B %Y')}  )

                month-=1
                if month == 0 :
                    month = 12
                    year-=1

            total_pages_in = 0
            total_pages_out = 0


            try :
                outox_info = transaction_history_viewer.get_mt_paginated( account_object=self.current_user, page=page_number, m_filter=current_month, y_filter=current_year )

                latest_transactions_sent = outox_info['records']
                total_pages_out = outox_info['total_pages']


                sent_transactions = { 'sent': latest_transactions_sent }

                transactions_sent = self.render_string('components/002l_sent.html',
                                                       transactions=sent_transactions,
                                                       total_number_of_pages_out=total_pages_out
                                                       
                                                       )
                inbox_info = transaction_history_viewer.get_mo_paginated( account_object=self.current_user, page=page_number, m_filter=current_month, y_filter=current_year )
                latest_transactions_inbox = inbox_info['records']
                total_pages_in = inbox_info['total_pages']
                total_number_of_pages =inbox_info['total_pages'] 
                
                
                transactions = {'inbox' : latest_transactions_inbox }

                transactions_inbox = self.render_string('components/002k_inbox.html',
                                                        total_pages_in=total_pages_in,
                                                        transactions=transactions,
                                                        total_number_of_pages=total_number_of_pages

                                                        )

            except Exception, e:
                transactions_inbox = ''
                transactions_sent = ''

                print 'transaction history exception raised %s' % e

            self.render('transaction_history.html',
                        date_filter_list=date_filter_list,
                        transactions_inbox=transactions_inbox,
                         transactions_sent=transactions_sent,
                         allow_inbox_next=allow_inbox_next,
                         allow_inbox_prev=allow_inbox_prev,
                         allow_sent_next=allow_sent_next,
                         allow_sent_prev=allow_sent_prev,
                         current_month_display=current_month_display,
                         total_pages_in=total_pages_in,
                         total_pages_out=total_pages_out,
                         current_month='%02d' % current_month,
                         current_year=current_year





                         )



        return

@route('/download-transactions/csv/([0-1][0-9])[\-_]([0-9]+)(/[0-9]+)?')
class DownloadCSVHandler( BaseHandlerSession ):

    @authenticated
    def get(self, month, year, mobile):


        if mobile :
            # strip out the leading slash
            mobile = mobile[1:]

        suffix = self.current_user.suffix
        if suffix :
            try:
                month = int(month)
                year = int(year)
                if year > int(datetime.now().strftime('%Y')) :
                    raise Exception('%s is in the future' % year)


                csv_data = transaction_history_viewer.generate_csv(  account_object=self.current_user, month=month, year=year, mobile=mobile)
                if csv_data :
                    filename = '%s_transactions_%s_%s.csv' % (suffix, month, year)

                    self.set_header('Content-Disposition', 'attachment; filename=%s' % filename )
                    self.set_header('Content-Type', 'application/force-download')
                    self.set_header('Content-Length', len(csv_data))
                    self.write( csv_data )
                else:
                    raise Exception('empty list')
            except Exception, e :
                print 'exception raised', e
                self.redirect('/dashboard')

        else :
            self.redirect('/dashboard')

@route('/download-transactions/xls/([0-1][0-9])[\-_]([0-9]+)(/[0-9]+)?')
class DownloadXLSHandler( BaseHandlerSession ):
    
    
    @authenticated
    def get(self, month, year, mobile):


        

        if mobile :
            # strip out the leading slash
            mobile = mobile[1:]

        suffix = self.current_user.suffix
        account_id = self.current_user.account_id
        if suffix :
            try:
                month = int(month)
                year = int(year)
                if year > int(datetime.now().strftime('%Y')) :
                    raise Exception('%s is in the future' % year)


                # start generate the xls file
                xls_file_full_path = transaction_history_viewer.gennerate_xls_file( account_object=self.current_user, month=month, year=year, mobile=mobile )
                
                
                filename = '%s_transactions_%s_%s.xls' % (account_id, month, year)
                
                buf_size = 4096
                self.set_header('Content-Type', 'application/octet-stream')
                self.set_header('Content-Disposition', 'attachment; filename=' + filename)
                with open(xls_file_full_path, 'r') as f:
                    while True:
                        data = f.read(buf_size)
                        if not data:
                            break
                        self.write(data)
                        
                transaction_history_viewer.cleanup_xls_file( full_path=xls_file_full_path )
                self.finish()
                
            except Exception, e :
                print 'exception raised', e
                self.redirect('/dashboard')

        else :
            self.redirect('/dashboard')


@route('/monthly-summary')
class MonthlyHistoryHandler( BaseHandlerSession ):

    @authenticated
    def get(self):

        formatted_summary = []

        total_sms_out = 0
        total_sms_in = 0
        total_sms_out_cost = 0
        total_sms_in_cost = 0
        try :

            sumarry = transaction_history_viewer.get_monthly_summary( account_object=self.current_user )


            month_keys = sumarry.keys()
            month_keys.sort( reverse=True )


            formatted_summary = []


            for m_key in month_keys:

                formatted_summary.append( sumarry[ m_key ]  )

                if sumarry[ m_key ].get('mo') :
                    total_sms_in+=sumarry[ m_key ]['mo']['sms_count']
                    total_sms_in_cost+=float(sumarry[ m_key ]['mo']['cost'])

                if sumarry[ m_key ].get('mt') :
                    total_sms_out+=sumarry[ m_key ]['mt']['sms_count']
                    total_sms_out_cost+=float(sumarry[ m_key ]['mt']['cost'])
        except Exception , e:
            print 'failed to fetch summary: %s' % e

        self.render('monthly_summary.html',
                        formatted_summary=formatted_summary,
                        total_sms_out = total_sms_out,
                        total_sms_in = total_sms_in,
                        total_sms_out_cost = total_sms_out_cost,
                        total_sms_in_cost = total_sms_in_cost

                        )
