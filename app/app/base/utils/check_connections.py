'''
basic tool used to check connections

connects to the specific servers defined in config

closes connections on success 

'''


import socket
import features.logging as chikka_sms_api_logger


def check_connections( config_values ):
    all_connected = True
    failed_connections = {}
    
    l = chikka_sms_api_logger.GeneralLogger()

    # configs should have  the respective 'host' and 'port' configs
    related_connections = {
                           'MYSQL' : config_values['mysql-db']['sms_api_config'] ,
                           'REDIS' : config_values['redis_servers']['sms_api'] ,
                           'SMART_PAYMENT_GATEWAY' : config_values['smart_payment_gateway']['redis_server'],
                           'MAILER' : config_values['mailer'],
                           'CREDITS_REDIS' : config_values['sms_credits']['redis_server']
                           
                           }

    # parse each fluentd config
    fluent_config = config_values['fluent_logger']
    for fluent_c_name, category_cfg in fluent_config.iteritems():
        related_connections[ 'FLUENT_%s' % fluent_c_name ] = category_cfg

    for c_name, cfg in related_connections.iteritems():
        connected = __check_specific( name=c_name, config=cfg, logger=l, failed_connections=failed_connections )
        all_connected = all_connected and connected        
        
    if not all_connected :
        l.error( 'NOT ALL SERVERS CONNECTED', failed_connections )
        return False
    return True


def __check_specific( name, config, logger, failed_connections ):
    '''
    checks a requred connection and logs the result
    @return: Boolean . if the connection is available
    
    '''
    
    connected = False
    
    logger.info( 'testing %s' % name )
    connected, message = check_connection( config['host'], config['port'] )
    message = '%s : %s' % ( name, message )
    if connected:
        logger.info( message )
        connected = True
    else:
        connected = False
        failed_connections[ name ] = config
        logger.error( message )
        
    return connected



def check_connection( host, port ):
    '''
    checks connection via the input host and port
    
    '''
    connection_available = False
    message = ''
    
    try:
        s = socket.socket()
        s.settimeout(5)
        
        
        s.connect((host, port))
        connection_available = True
        message = 'connection to %s:%s is available' % ( host, port )
        s.close()
    except socket.error, e:
        message = 'unable to connect to %s:%s : %s' % ( host, port, e )

    return connection_available, message

