/**
    @author: Jhesed Tacadena
    @date: 2014-02
    @description:
        - contains mootools implementation of 
        of UI team's jquery code for tutorial page
**/


var Views = function() {

}

var Model = function (){

}

var ControllersTutorial = function() {
        this.onClick = function() {
        
            /*
                Show/hide functions
            */
            
            $$(".com-help #update-your-api-settings").removeEvents();
            $$(".com-help #update-your-api-settings").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-api-settings")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #get-short-code").removeEvents();
            $$(".com-help #get-short-code").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-short-code")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #enroll-and-verify-your-test-mobile-number").removeEvents();
            $$(".com-help #enroll-and-verify-your-test-mobile-number").addEvent("click", function(e) {
                e.preventDefault();
                generic_open_dialog( $$(".com-tutorial-enroll-number")[0])
            });
            
            $$(".com-help #send-a-free-test-text-message").removeEvents();
            $$(".com-help #send-a-free-test-text-message").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-send-message")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #receive-test-text-message").removeEvents();
            $$(".com-help #receive-test-text-message").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-receive-message")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #buy-a-package-using-smart-payment").removeEvents();
            $$(".com-help #buy-a-package-using-smart-payment").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-smart-payment")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #manage-your-shopping-cart").removeEvents();
            $$(".com-help #manage-your-shopping-cart").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-manage-cart")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #view-your-transaction-history").removeEvents();
            $$(".com-help #view-your-transaction-history").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-transaction-history")[0].show();
                $$("#overlay").show();
            });
            
            $$(".com-help #buy-a-package-using-dragonpay").removeEvents();
            $$(".com-help #buy-a-package-using-dragonpay").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-dragonpay")[0].show();
                $$("#overlay").show();
            });

            
            $$(".com-help #view-your-purchase-history").removeEvents();
            $$(".com-help #view-your-purchase-history").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-purchase-history")[0].show();
                $$("#overlay").show();
            });

            
            /* smart payment */
            
            var pc_smartpayment = new PictureSlider($('pc-smart-payment'), [
                {
                    src: "static/img/tutorial_smart-payment_01.png",
                    content: '[image one]',
                    caption: '<p class="caption">Choose a package with quantity and add to your cart. Review the summary of your packages to check the items in your cart.</p><p class="page">Page 1 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_02.png",
                    content: '[image two]',
                    caption: '<p class="caption">Upon reviewing, you can proceed to checkout.</p><p class="page">Page 2 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_03.png",
                    content: '[image three]',
                    caption: '<p class="caption">Choose Smart Payment if you wish to buy your package using your Smart mobile number.</p><p class="page">Page 3 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_04.png",
                    content: '[image four]',
                    caption: '<p class="caption">You must read and agree to the Terms and Conditions before using the service.</p><p class="page">Page 4 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_05.png",
                    content: '[image five]',
                    caption: '<p class="caption">Click Proceed to Payment.</p><p class="page">Page 5 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_06.png",
                    content: '[image six]',
                    caption: '<p class="caption">Submit your Smart mobile number and you will receive a PIN code.</p><p class="page">Page 6 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_07.png",
                    content: '[image seven]',
                    caption: '<p class="caption">Use the PIN code for verification.</p><p class="page">Page 7 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_08.png",
                    content: '[image eight]',
                    caption: '<p class="caption">We will send you an SMS notification confirming your purchase.</p><p class="page">Page 8 of 9</p>',
                },
                {
                    src: "static/img/tutorial_smart-payment_09.png",
                    content: '[image nine]',
                    caption: '<p class="caption">Your Balance will be updated to include your new credits.</p><p class="page">Page 9 of 9</p>',
                }
            ], {
                    caption:
                    {
                        opacity: 1,
                    }
                }
            );
            
            $(document.body).getElement('.com-tutorial-smart-payment .next-lnk').addEvent('click', function(event) { event.preventDefault(); pc_smartpayment.right($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
            $(document.body).getElement('.com-tutorial-smart-payment .prev-lnk').addEvent('click', function(event) { event.preventDefault(); pc_smartpayment.left($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]);  });
            
            
            /* manage cart */
            
            var pc_managecart = new PictureSlider($('pc-manage-cart'), [
                {
                    src: "static/img/tutorial_manage-cart_01.png",
                    content: '[image one]',
                    caption: '<p class="caption">You can change the number of packages you are purchasing by editing the quantity.</p><p class="page">Page 1 of 4</p>',
                },
                {
                    src: "static/img/tutorial_manage-cart_02.png",
                    content: '[image two]',
                    caption: '<p class="caption">To remove a package from your cart, hover on the item and click delete icon.</p><p class="page">Page 2 of 4</p>',
                },
                {
                    src: "static/img/tutorial_manage-cart_03.png",
                    content: '[image three]',
                    caption: '<p class="caption">If you want more credits, click Add More Packages.</p><p class="page">Page 3 of 4</p>',
                },
                {
                    src: "static/img/tutorial_manage-cart_04.png",
                    content: '[image four]',
                    caption: '<p class="caption">To remove all the contents of your Cart, click Empty Cart.</p><p class="page">Page 4 of 4</p>',
                }
            ], {
                    caption:
                    {
                        opacity: 1,
                    }
                }
            );
            
            $(document.body).getElement('.com-tutorial-manage-cart .next-lnk').addEvent('click', function(event) { event.preventDefault(); pc_managecart.right($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
            $(document.body).getElement('.com-tutorial-manage-cart .prev-lnk').addEvent('click', function(event) { event.preventDefault(); pc_managecart.left($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]);  });
            
            
            /* transaction history */
            
            var pc_transactionhistory = new PictureSlider($('pc-transaction-history'), [
                {
                    src: "static/img/tutorial_transaction-history_01.png",
                    content: '[image one]',
                    caption: '<p class="caption">You can filter your transactions per mobile number and specific month.</p><p class="page">Page 1 of 3</p>',
                },
                {
                    src: "static/img/tutorial_transaction-history_02.png",
                    content: '[image two]',
                    caption: '<p class="caption">Click Inbox or Sent to view your message logs for the current month.</p><p class="page">Page 2 of 3</p>',
                },
                {
                    src: "static/img/tutorial_transaction-history_03.png",
                    content: '[image three]',
                    caption: '<p class="caption">You can also export your message logs in CSV file.</p><p class="page">Page 3 of 3</p>',
                }
            ], {
                    caption:
                    {
                        opacity: 1,
                    }
                }
            );
            
            var next = $(document.body).getElement('.com-tutorial-transaction-history .next-lnk').addEvent('click', function(event) { event.preventDefault(); pc_transactionhistory.right($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
            var prev = $(document.body).getElement('.com-tutorial-transaction-history .prev-lnk').addEvent('click', function(event) { event.preventDefault(); pc_transactionhistory.left($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
                  
                  
            /* purchase history */
            
            var pc_purchasehistory = new PictureSlider($('pc-purchase-history'), [
                {
                    src: "static/img/tutorial_purchase-history_01.png",
                    content: '[image one]',
                    caption: '<p class="caption">Click on the transaction ID to view your purchase details.</p><p class="page">Page 1 of 2</p>',
                },
                {
                    src: "static/img/tutorial_purchase-history_02.png",
                    content: '[image two]',
                    caption: '<p class="caption">You will see the breakdown of your packages purchase under that specific transaction.</p><p class="page">Page 2 of 2</p>',
                }
            ], {
                    caption:
                    {
                        opacity: 1,
                    }
                }
            );
            

            
            
            
            $(document.body).getElement('.com-tutorial-purchase-history .next-lnk').addEvent('click', function(event) {  event.preventDefault(); pc_purchasehistory.right($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
            $(document.body).getElement('.com-tutorial-purchase-history .prev-lnk').addEvent('click', function(event) {  event.preventDefault(); pc_purchasehistory.left($(this).parentNode.parentNode.children[1], $(this).parentNode.parentNode.children[0]); });
            
		
        }
            
                    
    /**
        Activates all events
    **/
    
    //for(ev in this)
    //    this[ev]();
}

window.addEvent('domready', function(){ 
    new ControllersTutorial();
});



	