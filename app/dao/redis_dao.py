'''
this file contains the base class for a redis-implemented DAO

implements basic functions of a DAO with redis commands

@author: vincent agudelo

'''


class BaseDAORedis( object ):
    
    redis_conn = None
    
    def __init__( self, redis_conn ):
        # this should always be set
        self.redis_conn = redis_conn
    