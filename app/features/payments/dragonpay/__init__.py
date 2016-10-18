from features.configuration import Configuration

general_config = Configuration.values()


# --- dragon pay ---

try:
    dragonpay_config = {'host': general_config['dragonpay']['host'],
                      'uri': general_config['dragonpay']['uri'],
                      'merchant_id': general_config['dragonpay']['merchant_id'],
                      'secret_key': general_config['dragonpay']['secret_key'],
                      'api_url': general_config['dragonpay']['api_url'], 
                      'api_get_token_url': general_config['dragonpay']['api_get_token_url'],
                      'min_amount_peso' : general_config['dragonpay']['min_amount_peso'] 
                    }
except Exception, e:
    # will only happen when used by standalone app
    # standalone app doesn't need this
    print e
    