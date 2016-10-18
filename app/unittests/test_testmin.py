
import gredis.client
from models.account import Account
from models.verification import Verification
from dao.account import AccountMySQLDAO
from utils.sql_tools import SQLUtils
from features.testmin import is_testmin_valid, \
    send_testmin_vercode, verify_testmin_vercode, \
    save_testmin, generate_code

        
"""
dbconn = SQLUtils(host=values[options.config]['mysql-db']['sms_api_config']['host'],
    port=values[options.config]['mysql-db']['sms_api_config']['port'],
    database=values[options.config]['mysql-db']['sms_api_config']['db'],
    user=values[options.config]['mysql-db']['sms_api_config']['user'],
    password=values[options.config]['mysql-db']['sms_api_config']['password'])

redisconn = gredis.client.Connection(address=str(values[options.config]['redis_servers']['sms_api_match']['host']), 
    port=int(values[options.config]['redis_servers']['sms_api_match']['port']))
"""

    
dbconn = SQLUtils(host='10.11.2.225',
    port=3306, database='sms_api',
    user='root', password='')

redisconn = gredis.client.Connection(
    address='10.11.2.238', port=6414)
    
redisconn.connect()

Account.dbconn = dbconn
Verification.dbconn = dbconn 
Verification.redisconn = redisconn

'''
    ERROR TESTS
'''

testmin = '09111111111'
user_id = '9'


# ---- PART 1: enroll -----------------

tm_response = is_testmin_valid(testmin) 

if tm_response['error']:
    print(tm_response['message'])
else:        
    # code = generate_code(user_id)

    sent_response = send_testmin_vercode(
        user_id=user_id, testmin=testmin)

    if sent_response['error']:
        print(sent_response['message'])

    else:    
        # ----- PART 2: VERIFICATION ------
        print sent_response['message']
        ver_response = verify_testmin_vercode(sent_response['code'],
            user_id, testmin)
        if ver_response['error']:
            print ver_response['message']
        else:
            print 'SUCCESSFUL VERIFICATION.'
