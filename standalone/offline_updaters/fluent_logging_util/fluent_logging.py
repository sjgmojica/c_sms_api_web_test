'''
util to execute logging via fluentd (td-client)
@author: vincent agudelo

'''

from fluent import sender
from tornado.options import define, options, parse_command_line, print_help
from utils.configuration import Configuration

define("config", default='debug', help="run configuration settings", type=str) 
define("log_method", default='file', help="file | scribe | both", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
define("port", default=80, help="run on the given port", type=int)

parse_command_line()
Configuration.initialize()
values = Configuration.values()      

output_to_terminal = True

# standalone checkout updater --> to expired

cfg = values['fluent_logger']['standalone_expired_checkout_deleter']

f_standalone_expired_checkout_deleter_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])
                                       
# standalone email

cfg = values['fluent_logger']['standalone_email_notification']

f_email_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])

# free to inactive
                                       
cfg = values['fluent_logger']['suffix_free_to_inactive']

f_suffix_free_to_inactive_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])

#  paid to inactive
                                       
cfg = values['fluent_logger']['suffix_paid_to_inactive']

f_suffix_paid_to_inactive_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])
      
# unpaid to inactive
      
cfg = values['fluent_logger']['suffix_unpaid_to_inactive']

f_suffix_unpaid_to_inactive_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])
                             
                             
def fluent_send( f_sender, tag, content  ):
    '''
    send to fluentd
    '''
    # data must be a dict
    
    f_sender.emit( tag, content )
    #event.Event( tag , content )
