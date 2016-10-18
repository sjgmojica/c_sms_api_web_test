'''
    @author: Jhesed Tacadena
    @date: 2013-11
'''

from cgi import escape 

def sanitize_html(content):
    '''
        @description:
            - wraps cgi escape method
            to a shorter version
            for template rendering purpose
    '''
    try:
        return escape(content).encode('ascii', 'xmlcharefreplace')
    except Exception, e:
        print e
        return content