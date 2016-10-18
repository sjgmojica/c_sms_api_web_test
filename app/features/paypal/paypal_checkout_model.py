from models.checkout import Checkout

from datetime import datetime

class PaypalPaymentCheckout( Checkout ):
    
    paypal_cache_dao = None
    
    @staticmethod
    def get( checkout_id ):
        '''
        overrides the traditional Checkout.get() to insert the checkout type
        
        
        '''
        
        return Checkout.db_dao.get( checkout_id=checkout_id, checkout_type=PaypalPaymentCheckout )
        
    
    
    def set_paypal_pending_payment_flag(self):
        
        PaypalPaymentCheckout.paypal_cache_dao.set_pending_paypal_payment_flag( account_id=self.account_id, checkout_id=self.checkout_id )
        
    @staticmethod
    def get_paypal_pending_payment_flag( account_id ):
        
        
        checkout_id = PaypalPaymentCheckout.paypal_cache_dao.get_pending_paypal_payment_flag( account_id=account_id )
        
        return checkout_id

    def clear_paypal_pending_payment_flag( self ):
        account_id = self.account_id
        
        checkout_id = PaypalPaymentCheckout.paypal_cache_dao.clear_pending_paypal_payment_flag( account_id=account_id )
        



    
    @staticmethod
    def get_total_purchases_current_month( account_id ):
        
        current_date = datetime.now()
        
        # using cache
        cache_result = PaypalPaymentCheckout.paypal_cache_dao.get_total_purchases_for_month( account_id=account_id, date_reference=current_date  )
        
        if cache_result is None:
            # 1. fetch from database
            total = PaypalPaymentCheckout.purchase_history_dao.get_total_purchase_per_month( account_id=account_id, date_reference=current_date )
            
            # 2 . rebult cache

            # make sure that the amount is integer (no decimal places)
            try:
                total = int(float(total))
            except Exception, e:
                raise Exception('invalid value to set monthly paypal purchase=%s . please use integer values. %s' % (total, e))            
            
            try:
                PaypalPaymentCheckout.paypal_cache_dao.set_total_purchases_for_month( account_id=account_id, date_reference=current_date, value=total )
                
            except Exception, e:
                print 'unable to set value', e
                pass
            
        else:
            total = cache_result 
        
        return total 

    @staticmethod
    def increment_monthly_paypal_purchase( account_id, date_reference, amount ):
        
        
        
        # make sure that the amount is integer (no decimal places)
        try:
            amount = int(float(amount))
        except Exception, e:
            raise Exception('invalid value to increment monthly paypal purchase=%s . please use integer values. %s' % (amout, e))

        redis_max_tries = 3
        cache_update = True
        
        w_try = 1
        while True and w_try <= redis_max_tries: 
            try:
                
                PaypalPaymentCheckout.paypal_cache_dao.increment_monthly_paypal_purchase( account_id=account_id, date_reference=date_reference, amount=amount )
                cache_update=True
                break
            except Exception, e:
                print 'unable to write for some reason: %s' % e
                w_try+=1
                pass
            

        if not cache_update :
            print 'cache not updated, deleting cache'
            #delete cache and hope for the best on next purchase
            PaypalPaymentCheckout.paypal_cache_dao.clear_monthly_paypal_purchase( account_id=account_id, date_reference=date_reference  )