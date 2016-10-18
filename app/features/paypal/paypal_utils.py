import sha

def get_paypal_callback_hash( account_id, checkout_id ):
    '''
    this will generate a hash to be used in paypal callback URL to execute payment
    there should be a way to make sure that the user that initiated the checkout
    is also the user that is logged-in when calling the callback url
    '''
 
    salt = 'ilovechikkaapi'

    hash = sha.new('%s%s%s' % (account_id, salt, checkout_id)  ).hexdigest()
    return hash