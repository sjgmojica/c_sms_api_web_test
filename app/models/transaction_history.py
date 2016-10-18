'''
transaction history model
@author: vincent agudelo

'''

from datetime import datetime

class TransactionHistory( object ):
    
    dao = None
    max_item_per_page = 5
    
    def __init__(self):
        
        
        pass
    
    @staticmethod
    def get_mo_history( client_id, from_datetime=None, to_datetime=None, items_per_page=None, page=1, mobile_filter=None, extra_row=0 ):
        '''
        @param from_datetime : Datetime . default is current datetime 
        @param to_datetime : Datetime . optional,
        @param items_per_page: integer .  can force number of items per page
        
        
        "mo" = "message origin"
        another way of saying "inbox messages"
        
        default from date is current date
        '''
        
        if not from_datetime :
            from_datetime = datetime.now()
            
        if not items_per_page:
            items_per_page = TransactionHistory.max_item_per_page
        
        items = TransactionHistory.dao.get_mo_logs( client_id, from_datetime=from_datetime, to_datetime=to_datetime, mobile_filter=mobile_filter,
                                                    items_per_page=items_per_page, page_number=page, extra_row=extra_row )
        
        return items 

    @staticmethod
    def get_mo_total_pages( client_id, from_datetime, to_datetime, items_per_page= 5 , mobile_filter=None):
        '''
        returns total number of pages for specified date range
        @param client_id: client_id that identifies owner of shortcode
        @param from_datetime: start date range
        @param to_datetime: to date range
        
        @return: non-negative Integer . may return 0 if no records are found
        
        '''
        
        return  TransactionHistory.dao.get_mo_total_pages( client_id=client_id, from_datetime=from_datetime, to_datetime=to_datetime, items_per_page=items_per_page,mobile_filter=mobile_filter)
    
    @staticmethod
    def get_mt_total_pages( client_id, from_datetime, to_datetime, items_per_page= 5 , mobile_filter=None, sms_type_filter='all'):
        '''
        returns total number of pages for specified date range
        @param client_id: client_id that identifies owner of shortcode
        @param from_datetime: start date range
        @param to_datetime: to date range
        
        @return: non-negative Integer . may return 0 if no records are found
        
        '''
        
        return  TransactionHistory.dao.get_mt_total_pages( client_id=client_id, from_datetime=from_datetime, to_datetime=to_datetime, items_per_page=items_per_page,mobile_filter=mobile_filter, sms_type_filter=sms_type_filter)

    
    @staticmethod
    def get_mt_history( client_id, from_datetime=None, to_datetime=None, items_per_page=None, page=1, mobile_filter=None, sms_type_filter='all', extra_row=0 ):
        '''
        "mt" = "message termination"
        another way of saying "sent"
        '''
        
        if not from_datetime :
            from_datetime = datetime.now()
            
        if not items_per_page:
            items_per_page = TransactionHistory.max_item_per_page        
        
        
        items = TransactionHistory.dao.get_mt_logs( client_id, from_datetime=from_datetime, to_datetime=to_datetime, items_per_page=items_per_page, page_number=page, mobile_filter=mobile_filter, sms_type_filter=sms_type_filter, extra_row=extra_row )
        return items


    @staticmethod
    def get_month_summary(client_id, month=None, year=None ):
        
        summary = {}
        
        
        summary = TransactionHistory.dao.get_month_sumarry( client_id=client_id, month=month, year=year  )
        
        #sanitize summary
        for month_y,month_v in summary.iteritems() :
            
            month_info = datetime.strptime(month_y, '%Y-%m')
            default_empty = { 'cost' : 0.0 , 'sms_count': 0 , 'month_name':   month_info.strftime('%B %Y')    , 'month_summary':month_y }
            
            #sanitize cost
            try:
                pass
                if month_v.get('mo', None):
                    month_v['mo']['cost'] = float(month_v['mo']['cost'])    
                    pass
                else:
                    # create empty result
                    month_v['mo'] = default_empty

            except Exception, e:
                print 'cound not sanitize [%s]: %s' % (month_v['mo']['cost'], e)

            try:
                if month_v.get('mt', None):
                    month_v['mt']['cost'] = float(month_v['mt']['cost'])
                    pass
                else:
                    # create empty result
                    month_v['mt'] = default_empty
            except Exception, e:
                print 'cound not sanitize [%s]: %s' % (month_v['mt']['cost'], e)
            
        
        return summary 