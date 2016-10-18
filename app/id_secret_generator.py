
from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str) 
define("log_method", default='file', help="file | scribe | both", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
define("port", default=80, help="run on the given port", type=int)

from gevent.monkey import patch_all; patch_all()
from gtornado.httpclient import patch_tornado_httpclient; patch_tornado_httpclient()
from features.configuration import Configuration    
from tornado.options import define, options, parse_command_line, print_help
from utils.sql_tools import SQLUtils

from utils.code_generation import *
parse_command_line()
Configuration.initialize()


from utils import code_generation

query = "SELECT id, suffix, email from accounts where client_id is null and status = 'ACTIVE' and suffix is not null"
update_query = "UPDATE accounts set client_id='%s', secret_key='%s' WHERE id='%s'"

def main():  
    values = Configuration.values()       
                
    print values
    dbconn = SQLUtils(host=values['mysql-db']['sms_api_config']['host'],
        port=values['mysql-db']['sms_api_config']['port'],
        database=values['mysql-db']['sms_api_config']['db'],
        user=values['mysql-db']['sms_api_config']['user'],
        password=values['mysql-db']['sms_api_config']['password'])
    
    result = dbconn.run_query(query_type="select", query=query, fetchall=True)
    
    q = []
    
    for r in result:
        client_id = create_sha256_signature(r['suffix'], r['email'])
        secret_key = create_client_id(r['email'])
        print client_id, secret_key, r['email']
        
        print update_query %(client_id, secret_key, r['id'])
        q.append(update_query %(client_id, secret_key, r['id']))
        dbconn.run_query("update", update_query, None, None)
        '-------------------------'
    
    for i in q:
        print i + ';'
    
main()