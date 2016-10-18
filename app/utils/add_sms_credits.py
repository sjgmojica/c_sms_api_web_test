'''
adds sms credtis to sms gateway
credits are per suffix
curent format to add credsit

@author: vincent agudelo

'''

from . import add_credit_config
import gredis.client

import time
from datetime import datetime

from utils.credits_locking import acquire_lock, release_lock        

credit_redisconn = gredis.client.Connection(  address=add_credit_config['redis_host'], 
                                       port=add_credit_config['redis_port']
                                       )

credit_redisconn.connect()

def add_credits( suffix, amount, charging ):
    '''
    @param suffix: STRING . the suffix where credits will be added  
    @param amount: FLOAT . amount (in PH Peso ) amount to add
    @param charging: DICT : mapping of service provider sms cost
    
    
    @return: String . the key (set member) used in adding credits. this will be used as a reference by the caller
    
    IT IS REQUIRED THAT SMART GLOBE and SUN appear in the mappings
    
    
    '''
    
    smart_cost = ''
    globe_cost = ''
    sun_cost = ''
    
    
    for carrier, cost in charging.iteritems():
        if carrier == 'SMART' : 
            smart_cost = cost
        elif carrier == 'GLOBE' :
            globe_cost = cost
        elif carrier == 'SUN' :
            sun_cost = cost
    
    key = 'SMSAPI_%s_CREDITS' % suffix 

    # multiply for granularity of score
    time_score = int(time.time()*1000000)

    #--- 2 decimal places are required for the values
    value = '%s:%0.2f:%0.2f:%0.2f:%.2f' % ( time_score, smart_cost, globe_cost, sun_cost,amount )
    
    result = None
    
    max_tries=3
    success=False
    try_run=1
    while success is False and try_run <= max_tries :
        try :
            result = credit_redisconn.zadd( key , value, time_score )
            if result :
                success = True
        
        except Exception, e :
            message = 'unable to write to key: %s : %s : %s ; %s' % (key, value, time_score, e)
            raise AddCreditError(  message )
        
        try_run+=1
        
    if success is False:
        message = 'unable to write to key: %s : %s : %s' % (key, value, time_score)
        print message
        raise AddCreditError(  message )
    

    max_tries=3
    success=False
    try_run=1
    
     
    while success is False and try_run <= max_tries :
    
        try :
            credit_redisconn.hset(  'SMSAPI_%s' % suffix , 'TRIAL_CREDITS', '0' )
            credit_redisconn.hset(  'SMSAPI_%s' % suffix , 'ACTIVE', '1' )
            credit_redisconn.hdel(  'SMSAPI_%s' % suffix , 'ZERO_CREDIT_DATE' )
            
            
            success = True
            
        except Exception, e :
            raise AddCreditError( 'unable to add credits: %s' % e )
        
        try_run+=1

    if result == 1 :
        return value
    else :
        return False
        


def get_balance( suffix ):
    '''
    @return: String . representation of the users balance (or empty string)
    @param suffix: the suffix of the user
    '''
    key = 'SMSAPI_%s_CREDITS' % suffix
    total_balance = 0 
    
    try:
        result = credit_redisconn.zrange( key , 0,-1  )
        # should be a list that looks something like
        # [ "138320867026911:0.30:0.45:0.35:499.70" , "138320908119896:0.30:0.45:0.35:500.00" ]
        temp_value = 0
        for credit_record in result :

            parsed = credit_record.split(':')
            # assumes that the balance is always at the top end (right most) of the list

            val = parsed.pop()
            temp_value += float( val )

        if temp_value :
            # format value
            total_balance = "%.2f" % temp_value
        
     
    except Exception, e:
        raise ReadCreditError( 'balance check error: %s %s' % (suffix, e) )
    
    return float(total_balance)
    

def  get_zero_credit_date( suffix ):
    '''
    retrieves date when account reached zero balance
    @return: datetime object | None
    
    '''
    
    
    zero_credit_date = None
    
    try:
        # acquire locking first
        credits_lock = acquire_lock( r_conn=redisconn, key='SMSAPI_%s_CREDITS' % suffix  )
        if credis_lock:
            key = 'SMSAPI_%s' % suffix
        
            zero_credit_date_str = credit_redisconn.hget( key , 'ZERO_CREDIT_DATE'  )
            if zero_credit_date_str :
                zero_credit_date = datetime.strptime( zero_credit_date_str, '%Y-%m-%d %H:%M:%S')
        
            release_lock( r_conn=redisconn, key='SMSAPI_%s_CREDITS' % suffix )


        else:
            raise ReadCreditError('unable to get credits, locked') 
        
    except Exception, e:
        raise ReadCreditError( 'unable to get zero credit date: %s %s' % (suffix, e) )
        # unable to execute retrieve zero credit date
    
    
    return zero_credit_date
    
    


class ReadCreditError( Exception ):
    pass

class AddCreditError( Exception ):
    pass
