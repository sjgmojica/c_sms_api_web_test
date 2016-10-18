import gredis.client

import gevent
import time

def acquire_lock(r_conn, key, lock_timeout=0.05, max_acquisition_attempts=3):
    current_timestamp = time.time

    lock_key = "lock.%s" % key
    lock_acquisition_attempts = 0
    locked = 0

    while not locked and (lock_acquisition_attempts < max_acquisition_attempts):
        locked = r_conn.setnx(lock_key, "%s" % (current_timestamp() + lock_timeout))
      
        if locked:
            return True
        else:
            try:
                current_lock_expiry = float(r_conn.get(lock_key))
                
                if current_lock_expiry < current_timestamp():
                    current_lock_expiry = float(r_conn.getset(lock_key, "%s" % (current_timestamp() + lock_timeout)))
                    if current_lock_expiry < current_timestamp():
                        return True

            except Exception:
                return False
       
        lock_acquisition_attempts += 1
        gevent.sleep(lock_timeout)

    return False

def release_lock(r_conn, key):
    lock_key = "lock.%s" % key
    released = r_conn.delete(lock_key)

    return (True if released else False)
