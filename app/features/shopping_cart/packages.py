'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from models.packages import Packages

def get_packages():
    '''
        @description:
            - returns ALL package objects
            from package table
    '''
    return Packages.get_all()
    
def get_package(id):
    return Packages.get(id)
  
