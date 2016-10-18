'''
initialization of modules

'''

from features.configuration import Configuration
from pprint import pprint


general_config = Configuration.values()



smart_payment_config = {
                        'serviceid' : general_config['smart_payment_gateway']['serviceid'],
                        'merchant_id' : general_config['smart_payment_gateway']['merchant_id'],
                        'redis_host' : general_config['smart_payment_gateway']['redis_server']['host'],
                        'redis_port' : general_config['smart_payment_gateway']['redis_server']['port'],
                        'transaction_queue_key' : general_config['smart_payment_gateway']['redis_server']['transaction_queue_key']
                        }

add_credit_config = {
                     'redis_host' :  general_config['sms_credits']['redis_server']['host'],
                     'redis_port' : general_config['sms_credits']['redis_server']['port'],
                     
                     }

text_api_config = {
                    'pincode_url' : general_config['text_api']['pincode_url'],
                    'mt_url' : general_config['text_api']['mt_url']
                    }


generic_mailer_settings = {'host': general_config['mailer']['host'], 
                           'port': general_config['mailer']['port'], 
                           'from_address': general_config['mailer']['mail_from_address'] }
                