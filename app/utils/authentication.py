'''
    taken from sir wacky
'''

from safeguard import AgentRSA
# import utils.redis_db as redis_db

import gredis.client
import M2Crypto
import hashlib
import base64

r_conn = None
decrypter = None

def get_public_key(suffix):
    hash_key = "SMSAPI_%s" % suffix

    if redis_db.acquire_lock(r_conn, hash_key):
        public_key = r_conn.hget(hash_key, "PUBLIC_KEY")
        redis_db.release_lock(r_conn, hash_key)
        return public_key

    return None

def validate_signature(public_key, signature, post_body):
    # original
    
    print '**************'
    print type(str(public_key))
    print str(public_key)
    print len(str(public_key))
    print '**************'
    print type(signature)
    print len(signature)
    print '**************'
    print type(post_body)
    print len(post_body)
    print post_body
    print '**************'
    
    try:
        agent_rsa = AgentRSA()
        temp_bio = M2Crypto.BIO.MemoryBuffer(str(public_key))
        temp_pub = M2Crypto.RSA.load_pub_key_bio(temp_bio)
        agent_rsa._pub_key = temp_pub
        return agent_rsa.verify_message(post_body, str(signature))
    
    except Exception, e:
        print '----------'
        print e
        print '----------'
        return False
        
        
    """
    
    # NO NEED NA TO. pang oldies to.
    
    try:
        # agent_rsa = AgentRSA()
        
        temp_bio = M2Crypto.BIO.MemoryBuffer(public_key)
        temp_pub = M2Crypto.RSA.load_pub_key_bio(temp_bio)
        pub_key = temp_pub
        
        signature = base64.b64decode(signature)
        digest = hashlib.new("sha512", message).digest()
        result =  pub_key.verify(digest, signature, "sha512")

        if result == 1:
            return True
        else:
            return False
    except Exception, e:
        return False
    """
    
def decrypt_message(post_body):
    return decrypter.decrypt_message(post_body)

"""   
# FOR TESTING. SHOULD RETURN 1
        
public_key1 = '-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAlsTvO2ubaZHkjKhp4wju\nzSffqP5CQVeQyWMkKnKHNJTx8ZxuXyFO2ZKJKAq7Oyz+qwBvakMfpc1lH2hcgSd+\nKMJy9Y8SPUT+ESON8/4Sc6IRp8u/gF2qCOZ9egx0O6L0DnSRJD3PTwvaHt6B/ssU\ne4ao+mYEAVU45Jg4KCnkBQ6B+srzB7yHFgFkjBS51N4YGg3dLlSfYvGbkK5VX/AW\nYDbJ+XgC/fPAhozazcecYfJI/tKOQd6SikBAQ/anVaQ7kDOonegndlYDyLKFchAa\n//+MtOjJPgY9AXY27V3JPBhfc/m4Rd2dLhMutow/GgkYLh0wlKKvMywgpjAYTze0\nUreXrju/gNzOh2WiRGVgxMeCYiktifAcJ6lBUz1QaiJnvCvf4eNMHvfx9W71ONlU\n1S4JhUGA0i7qbGPfIAT3P1lBK6YwWReRvGpg4riBNCksq9TGHtjzO/npsHs8mYTj\nrc/SfZuYfEW4CFKxKP32KRljhZEYEAVUT4818Q1lx0+118FU8An6Tp5eo6oOaeSu\nWdiyh91W0JrfT+vnvptqZABBKWzRDKkFnfnFGtzEq3v/fUaUwq0tNL90fMhAF8J3\nnAHqEtGoU8pP8MSE9K7tp42rKxttT5hxNXVl4BKAst46/KPxfHIjvr6NRIlTNKM/\nG1gZVAlkaW/Sgg/GAxCYFp8CAwEAAQ==\n-----END PUBLIC KEY-----\n'
# message = 'Hello'
# signature = 'hmYqXkHSAnUzopSBjb1MJaJSHfqRehRoAYjOhhiXYLmKCOk6Rx2Q+vE0x3NgscV3BYOYaFDCGeGgCNwL7bhHWJVglU66/8NaR3f6mlKAajznSYRuYRnkMLA4oO+uf8xrvKPNCTSpCCzbl97bZYWbq73fIF7xvoIp+QiH15Cxc/rtZ2PGVv4oz/akoiXeRatXImr9BwLjeCpOdoDTJZI72LHZ26quH+JHJm+x9RKISN9lmQ63PmZ2lAsYEGaWZsGabofwn7a5b/8tAuiFvz4HDA2kN+J/KcQlVhR4f8p62w5WCQaNA8g+M4VtSLQ7Ak3LNG7q/NfRJ/O5/Nu+q5pdQqsbuk6S4hxlF7I4KyIJ7Q9cqo8ka3MQ03PDrOjK+vjQMuV/AjZ4N1L81lHcELQ5ceGsKD/qY5jVv8ynShaYjzu8HxpZ0VVaagaEkRLeC5LVeqKFiZkYUTx75icnRWdrevhxJrZ5ZYtbWCoqLEINsVC2FNOqHDImOyqQ8DyHjrFULtdL+0WyltZuTFQMrUDVATMq/MX0pL5MBT2e7KkDu7qJ3fJW/J6at9RHnYMJLxL7M+IIpupzrgGAIB9pQrzNuTqyEa30qUgAcvMTzTKY+/BucRCbT4UeNl0vxMngweVG43Yr2o0cs3aYg92nr6RCZfk+HJeDX2nas5bWaCqIbzs='

message = 'Hello, welcome to Chikka API!'
signature = 'jXLHkD5RevRwUqRMM2bY0tQP6X0KDBQ6DKV0AiqBZuLzpbW/+BYnF9/JXeQvPFHq3SvMWYCyKZmUDsJ2+xkehJux0DzHR/RyDZZ4kYoVCcrumrdyiRmQUzovaBUfPFq2Pagfg2My8vaDR3aXGwdhaPLqBVyDXFfdEc3XdD3o2RaSCJqkuyEjxKP0wP2g+HOnpIdi6loFV0SfQ8pZY+3nwWWxPN1mGRUtG2QjNy43WW/+lB1x5u3VKbzCXqiM87PwT9MOhw5cNZBbIyFABFY/8uau5bQVVO/gQkv91ZLlGY0p3z+FbRvSqXIOXaUDuCIg3DROuNuezLkAaGjliBQ9Rls3iZ4h6slx+8rJGguXCFFa4SUcMp/SqCLnHy3bctzGdI9Xxq9FIRKGmU9gl7bbP6ZIlmx2L5Kn/jPnBLkoQxMN9dmskP3NzB2DzBFxkoknl0CP0VvGnb8FMVQ3crdu98BlMDoAix3mDeJF02w6TwWvnB4dcVTHoIOLc1V5uWT+xVcdMfJXtKEBhGfU/CUAWzFdFvD2P9AX7+JMq7GxnDt1iQQAJf+NBRC2OC6iWOjFp7E2TYMf5NVMDnp2NSEcDpWgDfM24/4pk4ilXywAmT4f2FonZ5dSbWQpnkWg18wp/QOL4DkttVW4BEJVFqUJsySQCE/mFcYMneyzJz6hk/M='

print validate_signature (public_key1, signature, message)
"""