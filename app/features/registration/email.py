'''
this module is in charge of email-related activities such as


check valid email format
send email for verification (registration / change email / change pssword)
 
@author: vincent agudelo
'''


import re2 as regex

def is_email_format_valid( email_address ):
    
    # should be in config
    max_length = 64
    
    
    if len(email_address) > max_length :
        
        return False
    
    # local part
    # no more than 64 charcaters long
    # alpha numeric
    
    # allowed special characters
    #  !#$%&'*+-/=?^_`{|}~
    
    # . (period is allowed as long as it is not the first
    
    
    #doman has max254 characters long
    # 63 characters between donmains
    # end must be 2 character loge
    
    #special_characters='[-!#\$%&\'\*\+/=\?\^`\{\}\|~\w]'
    
    #do not include single quote
    special_characters='[-!#\$%&\*\+/=\?\^`\{\}\|~\w]'
    
    
    #lolcal_with_quotes = r'("[^"]+?")'
    first_char = r'[0-9a-zA-Z]'
    next_char = r'(\.|%s)'%special_characters
    
    local_no_quotes = r'(%s%s%s*)' % (  first_char, next_char,next_char )
    
    #local_part_pattern = r'(%s|%s)'% ( lolcal_with_quotes, local_no_quotes  )
    # quoted local part no longer supported
    local_part_pattern = r'(%s)'% ( local_no_quotes  )
    
    
    
    #ipv4_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    #ip_address_domain_pattern = r'(\[%s\])' % ipv4_pattern
    
    domain_first_char_pattern = '([a-zA-Z0-9])'
    domain_next_chars_pattern = '[\.a-zA-Z0-9\-]*'
    
    sub_domain_pattern = '[]'
    
    domain_name = '(%s%s)' % (domain_first_char_pattern,domain_next_chars_pattern)
    
    
    # WILL NOT SUPPRT EMAIL THAT IS IN IP ADDRESS DOMAIN
    
    #domain_part_pattern = '(%s|%s)' % ( ip_address_domain_pattern, domain_name )
    domain_part_pattern =  domain_name
    
    rgx = '^%s(@)%s$' % (local_part_pattern, domain_part_pattern)
    
    email_checker = regex.compile(rgx, regex.IGNORECASE)
    if email_checker.match(email_address):
        
        
        
        return True
    
    return False


class InvalidEmailFormatError( Exception):
    pass

class SendEmailError( Exception ):
    
    email_to_send = None
    
    def __init__(self, email, message):
        
        self.email_to_send = email
        self.message = message
        
    def __str__(self):
        return 'unable to queue email for sending: %s; %s' %  ( self.email_to_send, self.message )
