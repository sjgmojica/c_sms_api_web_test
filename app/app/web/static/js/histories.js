/**
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - contains frontend implementations 
        for shopping cart processes.
**/

var ViewsHistories = { 

}

var ModelsHistories = function() {  

}

/**
    Controller (for events)
**/





function __get_details( param ){
    
    uri='/history/get-items/'+param
    
    var myRequest = new Request.JSON( {
        url:uri,
        data:{ 'json':'true' },
        method:'GET',
        onSuccess: function( response ){
            
            //-------------
            if (response.result == true){
                // load values
                var data_len = response.data.length
                var mytbody = $$('.com-purchase-details-table table tbody')[0]

                if ( $$('.com-purchase-details-table table tbody tr').length > 1 ){
                    mytbody.set('html',   mytbody.getChildren()[0].get('html') )
                }
                
                var template_row = $$('.com-purchase-details-table table tbody tr')[0]
                for ( var i=0 ; i< data_len ; i++){
                    
                    var row 
                    if ( i==0 ){
                        // get place holder
                        row = template_row
                    }
                    else{
                        // clone it and continue writing
                        row = template_row.clone(); 
                    }
                        
                    $$('.com-purchase-details.com-002q.ui-dialog .txt-title span')[0].set('text', param.substr(6))
                    
                    row.getElement('.plan-code').set('text', response.data[i].plancode)
                    row.getElement('.amount').set('text', 'P'+response.data[i].amount)
                    row.getElement('.qty').set('text', response.data[i].qty)
                    row.inject( mytbody )                    

                }

                //-------------------------
                // display
                generic_open_dialog( $$('.com-purchase-details.ui-dialog')[0]  )            
            
            }

            

        }
    }).send()    
    
}


function show_trans_detail( checkout  ){
    
    __get_details( checkout )
    
}




var ControllersHistories = function () { 


    /**
        Variable Definitions
    **/
    
    self.purchaseHistoryId = 'purchase_history_link';
    self.historyDismissDialogId = 'history_dismiss_dialog';
    self.transIds = 'div[id^=trans_]';
    
    /** 
        onclick Events 
    **/
    
    this.onClick = function () {
        
        /* purchase history */
              
        $$('a[id*=' + self.purchaseHistoryId + ']').removeEvents();
        $$('a[id*=' + self.purchaseHistoryId + ']').addEvent("click", function (e){
            e.preventDefault();
            transId = $(this).get('href');
            
            show_trans_detail( transId );

        });
    }
    
    /**
        Activates all events
    **/
    
    for(ev in this)
        this[ev]();
}

window.addEvent('domready', function(){ 
    var historyC = new ControllersHistories();
});

