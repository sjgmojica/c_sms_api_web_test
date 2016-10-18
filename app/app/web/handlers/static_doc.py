from tornado.web import authenticated, asynchronous
from app.web.handlers.web_base_handler import BaseHandlerSession
from app.base.utils.route import route



@route(['/docs/(overview)', '/docs/(using)', '/docs/(signature)', '/docs/(getting-started)', '/docs/(handling-messages)', '/docs/(references)'])
class SmsApiStaticDocsHandlerOverview( BaseHandlerSession ):
    
    @asynchronous
    def get(self, doc):
        '''
        simple handler that displays the docs page
        nothing special
        '''
        
        template_vars = {'overview_uri' : '/docs/overview', 'using_uri': '/docs/using',
            'signature_uri': '/docs/signature'}
        
        
        if doc =='overview' :
            self.render('docs/doc_overview.html', **template_vars)
        elif doc =='using':   
            self.render('docs/doc_using.html', **template_vars)
        elif doc =='signature':   
            self.render('docs/doc_signature.html', **template_vars)
        elif doc =='getting-started':
            #--- testing for template load
            
            
            template_path = self.application.settings['template_path']
            docs_code_example_path = '%s/docs/components/source_code_examples' % template_path
            
            code_src_map = {
                            'message_receiver_code' : 'message_receiver.html',
                            'message_sender_code' : 'message_sender.html',
                            'notification_receiver_code' : 'notification_receiver.html'
                            }
            
            for var_name,template_name in code_src_map.iteritems():
                template_vars[ var_name ] = self._get_rendered_plain_html( path_to_file = "%s/%s" % (docs_code_example_path, template_name) ) 


            
            self.render('docs/doc_getting-started.html', **template_vars)
            
        elif doc =='handling-messages':
            self.render('docs/doc_handling-messages.html', **template_vars)

        elif doc =='references':
            self.render('docs/doc_references.html', **template_vars)
            
    def _get_rendered_plain_html(self, path_to_file):
        """
        reads the template file "as is" and returns the result
        this function is intended for pure HTML ONLY
        """
        rendered_string = ''
        try :
            f = open( path_to_file )
            
            rendered_string = f.read()
            f.close()
            
        except:
            rendered_string = ''

        return rendered_string