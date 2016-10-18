'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

class Packages( object ):
    
    dao = None
      
    def __init__(self):
        self.plan_code = None
        self.plan_description = None
        self.amount = None
        self.credits = None
        self.days_valid = None  
        
    @staticmethod
    def get(plan_code):
        return Packages.dao.get(plan_code)
        
    @staticmethod
    def get_all():
        return Packages.dao.get_all()