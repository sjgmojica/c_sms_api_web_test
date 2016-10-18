
import gredis.client
from models.account import Account
from dao.account_mysql import AccountMySQLDAO
from utils.sql_tools import SQLUtils
from features.shortcode import update_suffix, \
    DuplicateSuffixException, update_acct_package, \
    generate_shortcode, generate_shortcode_list, \
    alpha_to_numeric, remove_used_codes

mysql_tool = SQLUtils(host='10.11.2.225',
    port=3306, database='sms_api',
    user='root', password='')
redisconn = gredis.client.Connection(
    address='10.11.2.238', port=6414)
redisconn.connect()

Account.dao = AccountMySQLDAO(sql_util=mysql_tool)

suffix = 7867
user_id = 9


print alpha_to_numeric(starts_with='abW1')
# print generate_shortcode()
  
code_list = [
    '222222', '1234', '40123', '8993', '123'
]

print remove_used_codes(code_list)

"""
suffix_generated = Account.check_suffix_list_availability(suffix_list=code_list)
print '------------------'
print suffix_generated
print '------------------'
"""
        
"""
print generate_shortcode_list()

try:
    update_suffix(user_id, suffix)

    # -- return before this if error 
    
    update_acct_package(user_id)

except DuplicateSuffixException, e:
    print e
"""
    