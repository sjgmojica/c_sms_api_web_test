from dao.purchase_history_mysql import PurchaseHistoryMysqlDAO

class PaypalPurchaseHistoryMysqlDAO( PurchaseHistoryMysqlDAO ):
    
    
    payment_type_value = 'PAYPAL'

    def get_total_purchase_per_month(self, account_id, date_reference  ):
        
        print 'get total purchase per type'
        print 1
        
        total = self._get_total_purchase_per_type_per_month( account_id=account_id, payment_type=self.payment_type_value, date_reference=date_reference  )
        print 2
        
        return total