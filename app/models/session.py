'''
this is the model that will represent a user's session with the application
@author: vincent agudelo
'''

from datetime import datetime


class Session( object ):
    
    cache_dao = None
    
    session_id = None
    account_id = None
    date_updated = None
    
    def __init__(self):
        
        pass
    
    @staticmethod
    def new( account_id ):
        '''
        creates session
        
        '''
        date_updated = datetime.now()
        
        new_session = Session()
        
        new_session.account_id = account_id
        new_session.date_updated = date_updated 
        
        new_session.session_id = new_session.__create_session_id(  ) 
        
        
        Session.cache_dao.save( account_id=account_id, session_id=new_session.session_id, date_updated=date_updated )
        
        return new_session


    @staticmethod        
    def get( account_id=None, session_id=None):
        '''
        retrieves session id
        can use either account_id or session_id
        
        '''
        
        if account_id or session_id:
            return Session.cache_dao.retrieve( account_id=account_id , session_id=session_id )
        else:
            return None


    def destroy(self):
        '''
        destroys current session
        
        @return: Boolean . wether or not the session was completely destroyed
        '''
        success = Session.cache_dao.destroy( account_id=self.account_id , session_id=self.session_id )
        
        return success
        

    
    
    def __create_session_id(self):
        '''
        creates the session id
        
        @todo: the hashing method must be hardened
        
        '''
        
        import hashlib
    
        hash = hashlib.md5()
        hash.update( '%s:%s' % (self.account_id, self.date_updated.strftime('%s') ) )
        encrypted = hash.hexdigest()

        return encrypted
        

        
        
class SessionError( Exception ):
    pass