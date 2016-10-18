'''
this is the DAO for Session that uses redis cache

'''

from models.session import Session, SessionError

from dao.redis_dao import BaseDAORedis
from datetime import datetime

class SessionRedisDAO( BaseDAORedis ):
    
    
    name = 'session cache'
    
    # the session key is 
    # example:
    #  session:web:1234
    # where 1234 is the account_id of the user
    # the content of the key will be the account updated and session id ( ':' separated)
    session_key_format = 'session:web:%s'
    
    # session by id saves session using the session id as key
    # example
    #   session_by_id:web:abcd1234abcd1234
    # it contains the date updated plus account id  ( ':' separated)
    session_by_id_key_format = 'session_by_id:web:%s'
    
    
    
    def save(self, account_id, session_id, date_updated ):
        '''
        saves the session to redis cache
        @param account_id: Integer . the account id of the user that owns the session
        @param session_id: String . the session id of the session
        @param date_updated: Datetime . the date time when the session is updated / created  
        '''
        
        try :
            
            self.redis_conn.mset({ 
                                  self.session_key_format % account_id : '%s:%s' % (date_updated.strftime('%s'), session_id),
                                  self.session_by_id_key_format % session_id : '%s:%s' % (date_updated.strftime('%s'), account_id),
                                  }
                                   )
            
        except Exception, e :
            
            raise SessionError( '%s : exception raised while trying to save session: %s' % (self.name, e)  )

    
    def retrieve( self, account_id=None, session_id=None ):
        '''
        retrieves the session id from cache
        
        '''
        
        
        
        try:
            
            # see how to get session, either by session id or by account id
            if account_id :
                
                session_return = Session()
                session_return.account_id = account_id
                
                raw_session = self.redis_conn.get( self.session_key_format % account_id  )
                if raw_session :
                
                    timestamp, session_id = raw_session.split(':')
                    session_return.session_id = session_id
                    session_return.date_updated = datetime.fromtimestamp( int(timestamp) )
                    
                    return session_return
                
            elif session_id :
                
                session_return = Session()
                session_return.session_id = session_id
                raw_session = self.redis_conn.get( self.session_by_id_key_format % session_id  )
                if raw_session :
                    timestamp, account_id = raw_session.split(':')
                    
                    session_return.date_updated = datetime.fromtimestamp( int(timestamp) )
                    session_return.account_id = account_id 
                
                    return session_return
            
            else:
                return None
            
        except Exception, e :
            raise SessionError( '%s : exception raised while trying to retrieve session: %s' % (self.name, e)  )
            
        
    def destroy(self, account_id, session_id):
        '''
        removes session keys from redis 
        
        '''
        
        destroyed = False
        
        try :
            
            key_1 = self.redis_conn.delete( self.session_by_id_key_format % session_id  )
            key_2 = self.redis_conn.delete( self.session_key_format % account_id  )
            
            print 'rsponse', key_1, key_2
            
            destroyed = True
            
        except Exception, e :
            
            raise SessionError( '%s : exception raised while trying to destroy session: %s' % (self.name, e)  )
            
            
        return destroyed
        
        