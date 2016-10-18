'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from urllib import urlencode
from urllib2 import Request, build_opener

def is_captcha_ok(recaptcha_challenge_field, 
    recaptcha_response_field, remote_ip, 
    private_key, verify_url):
    data = {
        'privatekey': private_key,
        'remoteip': remote_ip,
        'challenge': recaptcha_challenge_field,
        'response': recaptcha_response_field
    }
    try:
        return request(url=verify_url,
            data=urlencode(data), http_method="POST")
    except Exception, e:
        print e
    return False
            
def request(url, http_method, data=None):
    try:
        req = Request(url, data)
        req.get_method = lambda: http_method
        can_opener = build_opener()
        response = can_opener.open(req).read()
        return True if response.split("\n")[0] == "true" else False
    except HTTPError, e:
        print 'Cannot connect to recaptcha URL'
        raise e
    except Exception, e:
        raise e
        print e
    return False