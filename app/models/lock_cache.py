'''
    @author: Jhesed Tacadena
    @description:
        - contains locking function abstractions
        that can be used across apps
'''


class LockCache(object):

    dao = None
    
    @staticmethod
    def lock(key):
        return LockCache.dao.lock(key=key)
        
    @staticmethod
    def unlock(key):
        return LockCache.dao.unlock(key=key)