'''
this is where the fluent logger is initialized
the reason why it is in a separate directory is because it must be initialized 
independently from other utils. this is to avoid loading connections before the app starts

it was a case when loading the fluent logger util loads its parent util __init__.py which should
not be allowed

@author: vincent agudelo

'''

print 'init fluent logger'

from features.configuration import Configuration
from pprint import pprint


general_config = Configuration.values()


fluent_config = general_config['fluent_logger']
fluentd_config = {}

cfg = fluent_config['general']
fluentd_config['general_config'] = { 
                                    'tag':  cfg['tag'],  
                                    'host': cfg['host'], 
                                    'port':cfg['port'], 
                                    'verbose' : cfg['verbose']
                                    }
cfg = fluent_config['payment']
fluentd_config['payment_config'] = { 
                                    'tag':  cfg['tag'],  
                                    'host': cfg['host'], 
                                    'port':cfg['port'], 
                                    'verbose' : cfg['verbose']
                                    }

cfg = fluent_config['scart']
fluentd_config['scart_config'] = { 
                                    'tag':  cfg['tag'],  
                                    'host': cfg['host'], 
                                    'port':cfg['port'], 
                                    'verbose' : cfg['verbose']
                                    }
                  
