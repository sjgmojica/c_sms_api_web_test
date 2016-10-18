'''
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - a collection of URL helper functions
'''

from re import compile, IGNORECASE

VALID_URL_REGEX = compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', IGNORECASE)
  
  
def is_url_valid(url):
    '''
        @description:
            - returns True if url is valid,
            else False
    '''
    
    if VALID_URL_REGEX.match(url):
        return True
    return False