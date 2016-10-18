'''
util to execute logging via fluentd (td-client)
@author: vincent agudelo

'''

from fluent import sender


from . import fluentd_config

output_to_terminal = True

# general
cfg = fluentd_config['general_config']
f_general_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'])
# shopping cart
cfg = fluentd_config['scart_config']
f_shopping_cart_sender = sender.FluentSender( 
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'] )
# payment
cfg = fluentd_config['payment_config']
f_payment_sender = sender.FluentSender(  
                                       cfg['tag'],  
                                       host=cfg['host'], 
                                       port=cfg['port'], 
                                       verbose=cfg['verbose'] )




def fluent_send( f_sender, tag, content  ):
    '''
    send to fluentd
    '''
    # data must be a dict
    
    f_sender.emit( tag, content )
    #event.Event( tag , content )
