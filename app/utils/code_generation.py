'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''
from hashlib import sha256
from random import choice
from datetime import datetime
import murmur

RANDOM_STRING = 'ABCDEFGHJKMNPQRTUVWXYZ2346789'

def generate_code(length=6):
    '''
        returns a random 
        verification code
    '''
    rand_code = ''.join(choice(RANDOM_STRING)
            for i in range(length))
    return rand_code
    
def create_sha256_signature(suffix, email):
    '''
        @def
            - creates a sha 256 signature
            based from the parameters passed
    '''
    rand = generate_code(length=9)
    key_str = '%s:%s:%s:%s' %(
        suffix, email, 
        datetime.now().strftime('%Y%m%d%H%M%S'), 
        rand)
        
    print 'key: ', key_str, '---'
    print 'hashed: ', sha256(key_str).hexdigest()
    return sha256(key_str).hexdigest()

def create_client_id(email):
    '''
        @definition:
            - creates a murmurhash signature
    '''
    return sha256(email
        +datetime.now().strftime('%Y%m%d%H%M%S')
        +generate_code(length=9)).hexdigest()
    
"""
# TEST
suffix = '0347'
email = 'jdtacadena@chikka.com'

test_sig = create_sha256_signature(suffix, email)
test_murmur = create_client_id(email)

print '----------------------'
print test_sig
print len(test_sig)
print test_murmur
print '----------------------'

"""