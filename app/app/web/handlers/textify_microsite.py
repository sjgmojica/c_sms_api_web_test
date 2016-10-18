from tornado.web import asynchronous
from app.base.utils.route import route
from app.web.handlers.web_base_handler import BaseHandlerSession

from datetime import datetime


@route('/textify')
class ChangeEmailHandler( BaseHandlerSession ):
    
    @asynchronous
    def get(self):
        
        self.render('textify/index.html', copyright_year = self.__get_auto_copyright( year='auto' )  )
        
    def __get_auto_copyright(self, year='auto'):
        
        copy_right_year = ''
        
        curr_year = int(datetime.now().strftime('%Y'))
        
        try:
            year = int(year)
        except:
            year = 'auto'
        
        if year == 'auto' :
            copy_right_year = curr_year
        elif copy_right_year ==  str(curr_year) :
            copy_right_year = year

        elif year < curr_year :
            copy_right_year = '%s &ndash; %s' % (  year, curr_year  )
        
        elif year > curr_year :
            copy_right_year = curr_year
        
        
        return copy_right_year
        
