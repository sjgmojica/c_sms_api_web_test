'''
centralized tool for executing redis commands
@author: vincent agudelo

generally used to monitor (and centralize) redis command execution(s)

'''



def r_get( conn, key ):
    
    return __execute_redis_command( conn, 'get', key )

def r_incr( conn, key ):
    return __execute_redis_command( conn, 'incr', key )

def r_expire( conn, key, expire_seconds  ):

    return __execute_redis_command( conn, 'expire', key, expire_seconds )

def r_delete( conn, key ):

    return __execute_redis_command( conn, 'delete', key )

    
def __execute_redis_command( conn, command, *args, **kwargs ):
    '''
    generic function to call redis
    
    '''
    print 'execute redis command: %s( %s, "%s") ' % ( command, args, kwargs  ) 
    result = getattr( conn, command )( *args, **kwargs )
    
    return result
    