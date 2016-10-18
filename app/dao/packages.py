'''
    @author: Jhesed Tacadena
    @date: 2013-10
'''

from models.packages import Packages

TABLE_PACKAGE = 'packages'

class PackagesDao(object):
    
    def __init__(self, dbconn):
        self.dbconn = dbconn
        
    def get(self, id):
        criteria = {'id': id}
        table_cols = [
            'id', 
            'plan_code',
            'plan_description',
            'amount',
            # 'credits',
            'days_valid'
        ]
        
        try:
            result = self.dbconn.execute_select(
                table_name=TABLE_PACKAGE, conditions=criteria,
                table_cols=table_cols, fetchall=False)
            
            if result:
                package_object = self.as_object(result)
            return package_object
        
        except Exception, e:
            # to do
            print e
    
        return False
        
    def get_all(self):
        query_str = 'SELECT * FROM %s ORDER BY amount ASC' %TABLE_PACKAGE
        
        try:
            result = self.dbconn.run_query(
                query_type='select', query=query_str,
                fetchall=True)
           
            packages_list = []
            for package in result:
                if package and 'plan_code' in package and package['plan_code'] in ['PLAN 100', 
                    'PLAN 500', 'PLAN 1000', 'PLAN 2500']:  # be sure that it is the updated list of packages
                    packages_list.append(self.as_object(package))
        
        except Exception, e:
            # to do
            print e
    
        return packages_list
    
    def as_object(self, package):
        package_object = Packages()
        package_object.id = package['id']
        package_object.plan_code = package['plan_code']
        package_object.plan_description = package['plan_description']
        package_object.amount = package['amount']
        # package_object.credits = package['credits']
        package_object.days_valid = package['days_valid']
       
        return package_object
            