'''
generic mailer
@author: vincent agudelo
'''
from utils.send_mailx import send_mailx

from . import generic_mailer_settings

mailer_settings = generic_mailer_settings


def send_generic_mail( to_address, subject, body, mail_from=None ):
    
    
    if mail_from :
        email_from = mail_from
    else:
        email_from = mailer_settings['from_address']
    
    
    send_mailx(
               text_content=body, 
               html_content=body, 
               subject=subject, 
               to_=to_address,
                 
               email_from_ = email_from,
               mail_host=mailer_settings['host'], 
               mail_port=mailer_settings['port']
               )