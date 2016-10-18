"""
    Trimmed version of SmartNet's sql_util
    Uses umysqlpool instead of geventmysql
    due to bug
"""

from datetime import date, datetime
import time  
from umysqlpool import UltraSQLPoolConnection, Cursor
from MySQLdb import escape_string 
import warnings
import socket
import umysql
# from models.logger import Logger

class SQLUtils(object):
    ''' 
    Establishes SQL Connection on all DAO's
    Executes query statements
    Provides methods for constructing query strings. 
    '''
    __slots__ = ('sp_conn', 'ultrasql_cursor')
     
    def __init__(self
                ,host
                ,port
                ,database
                ,user
                ,password):    
        '''
        Construct an instance of SQLUtils and configure it to connect to MYSQL
        ''' 

        if not password:
            password = ''
        host = socket.getaddrinfo(host, 0)[2][4][0]
        conn = UltraSQLPoolConnection(host, port, user, password, database)
        self.ultrasql_cursor = Cursor(conn)
    
    def run_query(self, query_type, query, dictionary=None, fetchall=None):
        result = None    
        # print 'step 0' 
        # print self.ultrasql_cursor
        # print query
        try:
            self.ultrasql_cursor.execute(query)
        except umysql.SQLError, e:
            # print "HGERERQWEQWEQWE"
            # print "HELLO", e
            print e
	# print 'step 1'

	

        if query_type == 'select': 
            if fetchall:    
                ''' FETCHING ALL SELECT QUERY RESULT ''' 
                result = self.ultrasql_cursor.fetchall(dictionary=True)  
            else:  
                ''' FETCHING SINGLE SELECT QUERY RESULT ''' 
                result = self.ultrasql_cursor.fetchone(dictionary=True)  
        elif query_type == 'insert':
            if self.ultrasql_cursor.lastrowid:
                result = self.ultrasql_cursor.lastrowid 
            else:
                result = self.ultrasql_cursor.rowcount  
        
        elif query_type == 'update':        
            return self.ultrasql_cursor.rowcount
           
        else:
            result = True 
        

        if result: 
            return result
        else:
            return None  
        #except Exception, e:
        #    print e
            # Logger.logger.info('SQL ERROR %s %s' %(query, e))
                    
            
    def execute_update(self, table_name, params, conditions, 
                        operator="", limit=None, noquotes=None):
        '''
        Constructs and Executes SQL Query Update
        @param (table_name , String)
        @param (params , Dict)
        @param (conditions , Dict)
        @param (operator , String)
        @param (limit , String)
        @param (offset , String)
        
        1. table_name - table name that will be affected upon execution.
        2. params - dict of fields and values to be udpated.
        3. conditions - dict of where clause fields.
        4. operator - conditional operator to be used on conditions.
        '''    
        limit = '' if not limit else 'LIMIT %s' % str(limit) 
        #last_updated field is not pre-filled. needs to set the current datetime for this field

        # params['last_updated'] = datetime.now()

        column_vals = self.set_params(params, noquotes)
        condition_vals = self.set_condition(conditions, operator, noquotes)
        query_str = 'UPDATE %s set %s WHERE %s %s' % (table_name, column_vals,
                                                    condition_vals,limit) 
                                         
        return self.run_query('update', query_str, None, None )

    def execute_select(self, table_name, conditions, operator="", 
                    table_cols="*", fetchall=True, limit=None, 
                    offset=None, noquotes=None, orderby=None, order=None):
        '''
        Constructs and Executes SQL Query Select
        @param (table_name , String)
        @param (params , Dict)
        @param (conditions , Dict)
        @param (operator , String)
        @param (table_cols , List)
        @param (fetchall , Boolean)
        
        1. table_name - table name that will be affected upon execution.
        2. params - fields and values to be udpated.
        3. conditions - dict of where clause fields.
        4. operator - conditional operator to be used on conditions.
        5. fetchall - bool to tag if result would be a dict or list.
                    a. True - returns a list of dicts.
                    b. False - returns a dict.
        6. table_cols - List of field names to be returned.
        7. limit - number of records to display.
        8. offset - offsetting of the records to display
        '''
        
        limit = '' if not limit else 'LIMIT %s' % str(limit) 
        offset = '' if offset is None else 'OFFSET %s' % str(offset) 
        select_cols = self.set_columns( columns=table_cols )
        
        if conditions :
            condition_vals = self.set_condition(conditions, operator, noquotes, orderby, order)
            query_str = 'SELECT %s FROM %s WHERE %s %s %s' % (select_cols, table_name, condition_vals, limit, offset)
        else : 
            query_str = 'SELECT %s FROM %s %s %s' % (select_cols, table_name, limit, offset)
        
        
        
        
        
        result =  self.run_query('select', query_str, dictionary=True, fetchall=fetchall)
        return result
        
    def execute_insert_update(self, table_name, insert_params, 
                              update_params, noquotes=None): 
        '''
        Constructs and Executes SQL Query Insert & Update
        @param (table_name , String)
        @param (insert_params , Dict)
        @param (update_params , Dict) 
        
        1. table_name - table name that will be affected upon execution.
        2. insert_params - dict of field names and values to be inserted.
        3. update_params - dict of field names and values to be updated on key duplicate. 
        '''     


        #last_updated field is not pre-filled. needs to set the current datetime for this field
        # curdateobj = gmt_current_timestamp(given_date=None, sn_type=None)
        # update_params['last_updated'] = curdateobj['date_obj'].strftime("%Y-%m-%d %H:%M:%S")

        params = self.set_insert_values( insert_params ) 
        column_vals = self.set_params(update_params, noquotes)   
        query_string = "INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s" % (table_name, params['columns'], params['values'], column_vals)     
        return self.run_query('update', query_string , None, None )        

    def execute_insert(self, table_name, params): 
        '''
        Constructs and Executes SQL Query Insert
        @param (table_name , String)
        @param (params , Dict) 
        
        1. table_name - table name that will be affected upon execution.
        2. params - fields and values to be inserted.
        '''      
        params = self.set_insert_values(params) 
        query_str = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, params['columns'], params['values'])
        # print query_str
        return self.run_query('insert', query_str, None, None)
    
    def execute_delete(self, table_name, conditions, 
                       operator=None, noquotes=None):
        '''
        Constructs and Executes SQL Query Delete
        @param (table_name , String)
        @param (params , Dict)
        @param (conditions , Dict)
        @param (operator , String) 
        
        1. table_name - table name that will be affected upon execution.
        2. params - fields and values to be udpated.
        3. conditions - dict of where clause fields.
        4. operator - conditional operator to be used on conditions.
        '''    
        condition_param = self.set_condition(conditions, operator, noquotes)
        query_str = "DELETE from %s WHERE %s LIMIT 1" % (table_name , condition_param)
        return self.run_query('delete', query_str, None, None)
    
    def __set_call_params(self, kwargs):
        '''
        Builds stored procedure parameter string
        @param(kwargs, Dict)
        '''
        fields = [
            '_id',
            'email',
            'account_status',
            'sns_type',
            'sns_id',
            'np_id',
            'primary_mobile',
            'mobile',
            'mobile_status'
        ]
        values = []
        for field in fields: 
            gflag = False
            _val = None
            for k, v in kwargs.iteritems():
                if field == k:
                    gflag = True 
                    _val = v
            if gflag:
                if type(_val) is int: 
                    values.append(str(_val))
                else:
                    values.append('"' + str(_val) + '"')
            else: 
                values.append('null')
        values = ','.join(values) 
        return values
        
    def set_insert_values(self, params):
        '''
        Builds Insert statement value string
        @param(params, Dict)
        '''
        insert_fields = {}
        for k, v in params.iteritems():
            if v and v != None and v != 'None':
                v = self.escape_values(v)
                insert_fields[k] = v
                
        cols = ','.join(insert_fields.keys())
        vals = ','.join("\"%s\"" % (v) for v in insert_fields.itervalues())
         
        return {
            'values'  : vals  
            , 'columns': cols
        }
        
    def set_params(self, params, noquotes=None):
        '''
        Iterates on a dict and constructs a key=value format list
        @param(params , Dict)
        '''
        column_list = []
        column_vals = None

        for k, v in params.iteritems():
            if v is not None:
                v = self.escape_values(v)
                str_expr = "%s=\"%s\""
                if noquotes and type(noquotes)is list and k in noquotes:
                    str_expr = "%s=%s"
                column_list.append(str_expr % (k, v))
            else:
                column_list.append(("%s=NULL") % (k))
            # if v and v != None and v != 'None' and v != 'NULL': 
                # v = self.escape_values(v)
                # column_list.append(("%s=\"%s\"") % (k, v))
            # elif v == 'NULL' :
                # column_list.append(("%s=%s") % (k, v))
        temp_list = []
        for i in column_list:
            val = i
            if type(i) == unicode:
                val = i.encode('utf8')
            temp_list.append(val) 
        column_vals = ','.join( temp_list )
        return column_vals

    def set_condition(self, conditions, operator=" ", noquotes=None, orderby=None, order=None):
        '''
        Iterates on a dict and constructs a key=value + operator format list
        @param(conditions , Dict)
        @param(operator , String)
        @param(noquotes, List)
        @param(orderby, List)
        @param(order, String)
        '''    
        column_list = []
        column_vals = None 
        
        for k, v in conditions.iteritems(): 
            if type(v) is int or type(v) is long:
                column_list.append(("%s=%s") % (k, v))
            elif type(v) is tuple :
                # v[0] -> operator
                # v[1] -> value / field
                # i.e. `field > "value"`

                str_expr = "%s %s \"%s\""
                if noquotes and type(noquotes)is list and k in noquotes:
                    str_expr = "%s %s %s"
                column_list.append(str_expr % (k, v[0], v[1]))

            elif v is None:
                column_list.append("ISNULL(%s)" % k)
                
            else:
                str_expr = "%s=\"%s\""
                if noquotes and type(noquotes)is list and k in noquotes:
                    str_expr = "%s=%s"
                column_list.append(str_expr % (k, v))
        
        if len(conditions) > 1:  
            operator = " %s " % (operator)
            column_vals = operator.join(column_list) 
        else: 
            column_vals = column_list[0]
        
        if type(orderby) is list and len(orderby) > 0:
            orderby = ','.join(orderby)
            column_vals = "%s ORDER BY %s " % (column_vals, orderby)
            if order is not None:
                column_vals = "%s %s" % (column_vals, order)
            
        return column_vals

    def set_columns(self, columns=None):
        '''
        Joins a List by comma string
        @param(columns , List) 
        '''      
        cols = ''
        if type(columns) == list:
            cols = ','.join(columns) 
        elif type(columns) == dict:
            cols = ','.join(columns.keys())
        else:
            cols = columns
        return cols
    
    def datetime_to_string(self, data=None):
        '''
        Converts datetime objects to strings
        @param(data, List) 
        @param(data, Dict) 
        '''
        if data is not None: 
            if type(data) is dict:
                for k, v in data.iteritems():
                    if type(v) is datetime or type(v) is date or type(v) is time:
                        data[k] = str(v) 
            elif (type(data) is list or type(data) is tuple) and len(data) > 0: 
                for index, _data in enumerate(data):
                    for key, val in _data.iteritems():
                        if type(val) is datetime or type(val) is date or type(val) is time:
                            data[index][key] = str(val) 
        return data
    
    def escape_values(self, val):
        '''
        Standard MySQLdb escape_string library 
        Escapes quotes and double qoutes
        @param(val, (String, Int))
        '''
        try:    
            val = escape_string(val)
        except Exception:
            #if value is unicode, escape_string will raise an exception. only solution is to manually escape
            # the back slashes and double quotes to have a good query
            # the extra backslashes WILL NOT be in the resultting feild value saved in the database
            # this is only to format the query properly
            if type(val) is unicode or type(val) is str:
                #escape literal backslashes first
                val=val.replace('\\', '\\%s' % ('\\') )
                #escape the double quotes
                val=val.replace('"', '\\"')
        
            return val
        else:
            return val
