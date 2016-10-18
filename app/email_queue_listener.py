'''
stand-alone app to listen to email sending queue

usage

python email_queue_listener.py --config=debug --local_settings=true

@author: vincent agudelo

'''
from gevent.monkey import patch_all
patch_all()

import gredis.client
from tornado.options import define, options, parse_command_line, print_help


from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str) 
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
parse_command_line()
Configuration.initialize()

values = Configuration.values()



import features.logging as sms_api_logger

from models.account import Account
from models.verification import Verification
from utils.send_mailx import send_mailx

redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
redisconn.connect()

email_queue_key =  values['verify_email_queue_key']
l = sms_api_logger.GeneralLogger()

while True :

    try :
        # make sure that a new transaction id is used
        l.regenerate_new_trans_id()
        
        result = redisconn.brpop( email_queue_key )
        
        l.info('start processing queue item', result)

        if len( result ) == 2 :
            # verifi_id:email:verify type
            verifi_id, email, verifi_type = result[1].split(':')

            if verifi_id and email and verifi_type :

                #step 1 attempt to send email
                # get the content of email to send
                
                subject = '[chikka sms api] - verify email'
                if verifi_type == 'SIGNUP':
                    subject = 'Verify email address to start using Chikka API'
                elif verifi_type == 'CHANGEEMAIL':
                    subject = 'Verify email address to start using Chikka API'
                elif verifi_type == 'PASSWORD':
                    subject = 'You requested for password reset '
                
                key = 'emailcontent:%s'%verifi_id
                l.debug('retrieving email contents from cache', {'key', key})
                email_content = redisconn.get( key )
                
                if not email_content :
                    # in case content was eraseed
                    l.debug('missing email content, rebuilding', {'type': verifi_type })
                    verification_object = Verification.get( verification_id=verifi_id )
                    if verifi_type == 'SIGNUP':
                        email_content = verification_object.generate_signup_email_content()
                    elif verifi_type == 'CHANGEEMAIL':
                        email_content = verification_object.generate_change_email_verify_content()
                    elif verifi_type == 'PASSWORD':
                        email_content =  verification_object.generate_forget_password_content()

                html_content = email_content.replace("\n", '<br>')
            
                #--- mailer configs            
                mail_from = values['mailer']['mail_from_address']
                mailer_host = values['mailer']['host']
                mailer_port = values['mailer']['port']
                l.info('sending email', email)
                
                send_mailx(
                           text_content=email_content, 
                           html_content=html_content, 
                           subject= subject , 
                           to_=email,
                             
                           email_from_ = mail_from,
                           mail_host=mailer_host, 
                           mail_port=mailer_port
                           )
    
                # after sending, delete email content cache
                
                content_cache_key = 'emailcontent:%s'%verifi_id 
                l.debug('deleting email content cache', {'key': content_cache_key})
                redisconn.delete( content_cache_key )
    
                # step 2 if no complaint, update verification, set send_status to 'SENT'
                l.info('email sent')
                Verification.set_send_status_sent( verification_id = verifi_id)            
                
    except Exception, e:
        l.error('exception rasied while processing email queue item', e)        