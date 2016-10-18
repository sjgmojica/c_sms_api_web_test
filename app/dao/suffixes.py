'''
    @author: jhesed tacadena
    @year: 2013
'''

from models.suffixes import Suffixes, DuplicateSuffixException

class SuffixesDao(object):
    def __init__(self, dbconn):
        self.dbconn = dbconn
            
    def get_suffix(self, suffix):
        criteria = {'suffix': suffix}
        table_cols = ['id']
        try:
            return self.dbconn.execute_select(
                table_name='accounts', 
                conditions=criteria,
                table_cols=table_cols, 
                fetchall=False)  
        except Exception, e:
            print e
            raise e
        return False    
    
    def has_suffix(self, account_id):
        criteria = {'account_id': account_id}
        table_cols = ['suffix']
        try:
            return self.dbconn.execute_select(
                table_name='claimed_suffixes', 
                conditions=criteria,
                table_cols=table_cols, 
                fetchall=False)  
        except Exception, e:
            print e
            raise e
        return False    
        
    def set_suffix(self, account_id, suffix):
        criteria = {'account_id': account_id}
        params = {'suffix': suffix}
        try:
            if self.is_user_has_suffix(account_id):
                self.dbconn.execute_update(
                    table_name='claimed_suffixes', params=params, 
                    conditions=criteria)
            else:
                params['account_id'] = account_id
                self.dbconn.execute_insert(
                    table_name='claimed_suffixes', params=params)
                    
        except Exception, e:
            if 'Duplicate entry' in str(e):
                if "for key 'suffix'" in str(e):
                    raise DuplicateSuffixException(suffix=suffix)
            else:
                raise e
        
    def check_suffix_list_availability(self, suffix_list):
        query_str = ''
        for suffix in suffix_list:
            query_str += "SELECT suffix FROM claimed_suffixes \
                WHERE suffix='%s' UNION " %(suffix)
        # removes the last word UNION from query string
       
        if query_str:  # suffix_list may be empty
            query_str = query_str[:-6] 
            try:
                return self.dbconn.run_query('select', query_str,
                    dictionary=False, fetchall=True)   
            except Exception, e:
                print e
                raise e
        return False
    
    def is_user_has_suffix(self, account_id):
        criteria = {'account_id': account_id}
        table_cols = ['suffix']
        try:
            suffix = self.dbconn.execute_select(
                table_name='claimed_suffixes', 
                conditions=criteria,
                table_cols=table_cols, 
                fetchall=False)
            if suffix and 'suffix' in suffix:
                return suffix['suffix']
        except Exception, e:
            print e
            raise e
        return False    