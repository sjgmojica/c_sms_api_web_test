'''
    @author: jhesed tacadena
    @year: 2013
'''

class Suffixes(object):
    dao = None
    
    @staticmethod
    def get_suffix(suffix):
        return Suffixes.dao.get_suffix(suffix)
        
    @staticmethod
    def has_suffix(account_id):
        return Suffixes.dao.has_suffix(account_id)
        
    @staticmethod
    def check_suffix_list_availability(suffix_list):      
        return Suffixes.dao.check_suffix_list_availability(suffix_list)
        
    @staticmethod
    def set_suffix(account_id, suffix):
        return Suffixes.dao.set_suffix(account_id, suffix)
        
    @staticmethod
    def is_user_has_suffix(account_id):
        return Suffixes.dao.is_user_has_suffix(account_id)
        
    
class DuplicateSuffixException(Exception):
    '''
        Custom exception triggered
        when inserting duplicate
        suffixes in table
    ''' 
    
    error_spiel = 'Suffix %s already already taken'
   
    def __init__(self, suffix):
        self.suffix = str(suffix)
    
    def __str__(self):
        return self.error_spiel % self.suffix
           