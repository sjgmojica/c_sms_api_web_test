/**
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - contains frontend implementations
        for shopping cart processes.
**/


/**
    Views (for rendering dynamic ajax templates)
**/

var ViewsShoppingCart = {

    checkout : function(cartItems, totalCost, enable_dragonpay, enable_paypal, paypal_limit_reached, enable_paymaya) {

        // determines if dragonpay option will be available in checkout
        var _set_dragon_pay_enabled=true
        _set_dragon_pay_enabled = typeof enable_dragonpay !== 'undefined' ? enable_dragonpay : false
        _set_paypal_enabled = typeof enable_paypal !== 'undefined' ? enable_paypal : false
        _set_paymaya_enabled = typeof enable_paymaya !== 'undefined' ? enable_paymaya : false


        var dragonpay_option = ''
        if ( _set_dragon_pay_enabled ){

            dragonpay_option = '<td><div class="fld-item-payment"><input value="DRAGONPAY" id="payment-two" type="radio" name="radio"><label for="payment-two">Dragonpay</label></div></td>';
        }

        var paymaya_option = ''
        if (_set_paymaya_enabled) {
            paymaya_option = '<td><div class="fld-item-payment"><input value="PAYMAYA" type="radio" name="radio"><label>VISA/Mastercard</label></div></td>';
        }


        var paypal_option = ''
        if ( _set_paypal_enabled ){
            paypal_option = '<td><div class="fld-item-payment"><input value="PAYPAL" id="payment-two" type="radio" name="radio"><label>PayPal™</label></div></td>';
        }


        html = '<div class="com-checkout-cr">'
            + '            <header>'
            + '                <h1 class="assistive-text">Checkout</h1>'
            + '                <p class="txt-title">Checkout</p>'
            + '                <div id="procede_checkout_error" class="notification notification-error notification-inline" style="display:None;">'
            + '                    <p class="notification-message">Please read and agree to the Terms and Conditions before proceeding to checkout.</p>'
            + '                </div>'
            + '                <!-- Dismiss link -->'
            + '    <p class="dismiss-link-cr"><a id="dismiss_dialog" class="dismiss-link" href="#"><span class="lbl">Dismiss</span></a></p>        </header>'
            + '            <div class="com-checkout-ct">'
            + '                <form action="/cart/payment" method="post" class="com-checkout-frm">'
            + '                  <input type="hidden" name="paypal_limit_reaced" value="'+paypal_limit_reached+'">                '
            + '                  <input type="hidden" name="max_paypal_purchase" value="yyy">'
            + '                  <input type="hidden" name="max_paypal_purchase_formatted" value="yyy">'
            + '                  <input type="hidden" name="has_pending_paypal_purchase" value="false">'
            + '                  <input type="hidden" name="current_paypal_purchase" value="zzz">'
            + '                  <input type="hidden" name="current_paypal_purchase_formatted" value="zzz">'
            + '                 <fieldset>'
            + '                     <legend>Checkout</legend>'
            + '                        <p class="txt-desc">Here\'s a summary of the plans you have chosen.</p>'
            + '                        <div class="checkout-table">'
            + '                            <table cellpadding="5" border="0">'
            + '                                <thead>'
            + '                                    <tr>'
            + '                                        <th>Item</th>'
            + '                                        <th>Quantity</th>'
            + '                                        <th>Total</th>'
            + '                                    </tr>'
            + '                                </thead>'
            + '                                <tbody>';

                                                for (var i=0; i<cartItems.length; i++) {
                                                    amount = parseFloat(cartItems[i]['amount']) * parseInt(cartItems[i]['quantity']);
                                                    html += '<tr>'
                                                        + '<td class="item">' + cartItems[i]['plan_code'] + '</td>'
                                                        + '<td class="qty">' + cartItems[i]['quantity'] + '</td>'
                                                        + '<td class="total"> P' + amount + '</td>'
                                                        + '</tr>'
                                                }

        html += '                                    <tr class="total">'
            + '                                     <td class="label">Total Amount</td>'
            + '                                        <td class="amount" colspan="2">'
            + '                                            P' + totalCost + ''
            + '                                        </td>'
            + '                                    </tr>'
            + '                                </tbody>'
            + '                            </table>        '
            + '                        </div>'
            + '                        <div class="payment-cr">'
            + '                         <p class="txt-title">Payment Options</p>'
            + '                         <p class="txt-desc">[Payment Options description]</p>'
            + '                             <div class="fld fld-payment">'
            + '                                 <table width="100%">'
            + '                                     <tr>'
            + '                                         <td>'
            + '                                             <div class="fld-item-payment">'
            + '                                                 <input value="SMART" id="payment-one" type="radio" name="radio" checked>'
            + '                                                 <label for="payment-one">Smart Payment</label>'
            + '                                             </div>'
            + '                                         </td>'
            +                                           dragonpay_option
            + '                                     </tr>'
            + '                                     <tr>'
            + paymaya_option
            + paypal_option
            + '                                     </tr>'
            +                                   '</table>'
            + '                             </div>'
            + '                        </div>'
            + '                        <div class="fld fld-terms">'
            + '                            <div class="fld-item-terms">'
            + '                                <input id="terms" type="checkbox">'
            + '                                <label for="terms">You must agree to the <a id="terms_link" class="terms-lnk" href="#">Terms and Conditions</a> before you can proceed to payment.</label>'
            + '                            </div>                                            '
            + '                        </div>'
            + '                        <div class="fld fld-axn">'
            + '                            <div class="psu-btn psu-btn-pri psu-btn-sub">'
            + '                                <button id="procede_checkout" class="btn-sub" type="submit">Proceed to Payment</button>'
            + '                            </div>'
            + '                            <div class="psu-btn psu-btn-neg psu-btn-cncl">'
            + '                                <a id="dismiss_dialog" class="cncl-lnk" href="#"><span class="lbl">Cancel</span></a>'
            + '                            </div>'
            + '                        </div>'
            + '                 </fieldset>'
            + '             </form>'
            + '           </div>'
            + '       </div>';

            $('ui_dialog').set('html', html);

            // add event to the form
            $$('form')[0].addEvent('submit', function(e){
                // disable after clicking
                $(self.procedeCheckoutId).set('disabled', true);


                if ( $$('input[name*=rad]:checked' )[0].value =='PAYPAL'){

                    var current_paypal_purchases = parseInt($$('input[name*=current_paypal_purchase]')[0].value)
                    var current_paypal_purchases_formatted = $$('input[name=current_paypal_purchase_formatted]')[0].value

                    var max_paypal_purchases = parseInt($$('input[name*=max_paypal_purchase]')[0].value)
                    var max_paypal_purchases_formatted = $$('input[name=max_paypal_purchase_formatted]')[0].value


                    var current_purchased_spiel = 'and you have already purchased P'+current_paypal_purchases_formatted

                    var paypal_err_msg1 = 'The monthly limit for Paypal purchase is P'+max_paypal_purchases_formatted
                    var paypal_err_msg2 = 'You can no longer purchase credits via Paypal for this month. The limit for Paypal purchase is P'+max_paypal_purchases_formatted+'/month. Kindly choose another payment option.'

                    var kindly_purchase_smaller_spiel = 'Kindly purchase a smaller amount.'

                    var has_existing_pending_paypal_purchase = $$('input[name*=has_pending]')[0].value

                    var has_existing_pending_paypal_spiel = 'You have a pending Paypal purchase request. Please try again in a few minutes or choose another payment method.'

                    console.log(current_paypal_purchases)
                    console.log(max_paypal_purchases)
                    console.log( current_paypal_purchases >= max_paypal_purchases )

                    // if user already has max paypal purchases for current month
                    if ( current_paypal_purchases >= max_paypal_purchases ) {
                        e.preventDefault()
                        $('procede_checkout_error').getElement('p.notification-message').set('text', paypal_err_msg2 )
                        $('procede_checkout_error').setStyle('display', 'block')
                    }
                    // if intended purchase > max paypal limit per month
                    else if ( parseInt(totalCost) > max_paypal_purchases && current_paypal_purchases == 0 ){
                        e.preventDefault()
                        $('procede_checkout_error').getElement('p.notification-message').set('text', paypal_err_msg1+'. '+kindly_purchase_smaller_spiel )
                        $('procede_checkout_error').setStyle('display', 'block')
                    }
                    // if intended purchase PLUS current purchase is about max of paypal payment per month
                    else if ( parseInt(totalCost)+parseInt( current_paypal_purchases ) > max_paypal_purchases ){
                        e.preventDefault()
                        $('procede_checkout_error').getElement('p.notification-message').set('text', paypal_err_msg1+' '+current_purchased_spiel+'. '+kindly_purchase_smaller_spiel )
                        $('procede_checkout_error').setStyle('display', 'block')
                    }
                    else if ( has_existing_pending_paypal_purchase == "true" ){
                        e.preventDefault()
                        $('procede_checkout_error').getElement('p.notification-message').set('text', has_existing_pending_paypal_spiel )
                        $('procede_checkout_error').setStyle('display', 'block')

                    }
                }
            })




            // add event when selecting a radio button, the submit button will re-enable
            $$('input[name*=rad]' ).addEvent('click', function(e){
                $(self.procedeCheckoutId).set('disabled', false);
            })


            new ControllersShoppingCart(); /* adds events to ajax calls @todo: REVISE THIS. */
            new Controller(); /* adds events to ajax calls @todo: REVISE THIS. */
    },
}


/**
    MODEL (for ajax calls)
**/

var ModelsShoppingCart = function() {

    /**
        Variable Definitions
    **/

    self.purchaseCounterId = 'purchase_counter';

    /**
        Ajax Function definitions
    **/

    this.cartAdd = function (onSuccess){

        /* adds to cart */

        new Request.JSON(
        {
            'url' : '/cart/add',
            'method' : 'POST',
            'data' : {
                'plan_id' : plan,
                'plan_code' : planCode,
                'quantity' : quantity
                // 'amount' : amount
                // 'credits' : credits,
                // 'days_valid' : daysValid
            },
            'onSuccess' : function(response) {
                $$('.com-purchase-package .notification').hide()
                $(self.purchaseCounterId).set('html', response.count);
                $$('.com-purchase-package .notification-success p.notification-message').set('html', response.message);
                $$('.com-purchase-package .notification.notification-success').setStyle('display', 'block');
            }
        }).send();
    }

    this.checkout = function (onSuccess){

        /* checkout items in cart */

        new Request.JSON(
        {
            'url' : '/cart/checkout',
            'method' : 'POST',
            'data' : {
                'plan_quantities': String.from(planQuantities + ',')
            },
            'onSuccess' : function(response) {
                cartItems = response['cart_items'];
                totalCost = response['total_cost'];
                enable_dragon_pay = response['enable_dragon_pay']
                enable_paypal = response['enable_paypal']
                enable_paymaya = response['enable_paymaya']
                if ( ! response['allowed_total_paypal_purchases'] ){

                    paypal_limit_reached = true
                }
                else{
                    paypal_limit_reached = false
                }



                if (onSuccess) {
                    onSuccess(cartItems, totalCost, enable_dragon_pay,enable_paypal, paypal_limit_reached, enable_paymaya );

                    $$('input[name*=max_paypal_purchase]')[0].set('value', response['max_paypal_purchases'])
                    $$('input[name*=current_paypal_purchase]')[0].set('value', response['current_paypal_purchases'])

                    $$('input[name*=has_pending]')[0].set('value', response['has_pending_paypal_purchase'])


                    $$('input[name=current_paypal_purchase_formatted]')[0].set('value', response['current_paypal_purchases_formatted'])
                    $$('input[name=max_paypal_purchase_formatted]')[0].set('value', response['max_paypal_purchases_formatted'])


                }
                else {
                    window.location = '/cart';
                }
            }
        }).send();
    }
}

/**
    Controller (for events)
**/

var ControllersShoppingCart = function () {

    var m = new ModelsShoppingCart(),
        v = ViewsShoppingCart;


    self.uiDialogId = 'ui_dialog';

    /**
        Variable Definitions
    **/

    /* shopping cart */

    self.addToCartId = 'addToCart';
    self.purchaseFormId = 'addToCart';
    self.purchaseCounterId = 'purchase_counter';
    self.wipeOutCartId = 'cart-wipeout';

    self.planId = 'plan_id';
    self.planCodeId = 'plan_code';
    self.quantityId = 'quantity';
    self.amountId = 'amount';
    self.creditsId = 'credits';
    self.daysValidId = 'days_valid';
    self.planQuantityId = 'plan_qty';
    self.totalId = 'total';
    self.totalCostId = 'total_cost';
    self.amountPerQuantity = 'amount-per-quantity';
    self.termsAndConditionId = 'terms';
    self.termsAndConditionLinkId = 'terms_link';
    self.procedeCheckoutId = 'procede_checkout';
    self.procedeCheckoutErrorId = 'procede_checkout_error';
    self.checkoutId = 'checkout';
    self.addMorePackagesId = 'add-more-packages';

    self.intRegex = /^\d+$/;
    self.isLastPriceInt = true;
    self.lastPrice = null;

    /* checkout */

    self.cartIds = 'cart_ids';
    self.pincodeId = 'cart_pincode';

    self.purchaseCtr = 1;

    /**
        On click Events
    **/

    this.onClick = function() {

        /* adds to cart */

        $$('button[id=' + self.addToCartId + ']').removeEvents();
        $$('button[id=' + self.addToCartId + ']').addEvent("click", function (e){
            e.preventDefault();
            self.purchaseCtr++;
            $(self.purchaseCounterId).set('html', '<span>' + self.purchaseCtr + '</span>');

            plan = this.getParent('form').getElementById(self.planId).value;
            planCode = this.getParent('form').getElementById(self.planCodeId).value
            quantity = this.getParent('form').getElementById(self.quantityId).value;
            amount = this.getParent('form').getElementById(self.amountId).value;
            credits = this.getParent('form').getElementById(self.creditsId).value;
            daysValid = this.getParent('form').getElementById(self.daysValidId).value;
            m.cartAdd();
        });

        /* proceed to checkout after shopping cart */

        if($(self.checkoutId) != null){
            $(self.self.checkoutId).removeEvents();
            $(self.self.checkoutId).addEvent('click', function(e){
                e.preventDefault();

                cart_ids = $(self.cartIds).value;
                cart_ids = JSON.parse(cart_ids);
                planQuantities = []
                for (var i=0; i<cart_ids.length; i++){
                    pq = self.planQuantityId + cart_ids[i];
                    plan = {
                        'id' : cart_ids[i],
                        'quantity': $(pq).value
                   }
                   planQuantities.push(JSON.encode(plan) + '|'); /* used for serverside parsing later */
                }
                m.checkout(v.checkout); /* displays  cart items after ajax request */
                $(self.uiDialogId).setStyle('display', 'block');
                $(self.overlayId).setStyle('display', 'block');
            });
        }

        if($(self.addMorePackagesId) != null){
            $(self.self.addMorePackagesId).removeEvents();
            $(self.self.addMorePackagesId).addEvent('click', function(e){
                e.preventDefault();

                cart_ids = $(self.cartIds).value;
                cart_ids = JSON.parse(cart_ids);
                planQuantities = []
                for (var i=0; i<cart_ids.length; i++){
                    pq = self.planQuantityId + cart_ids[i];
                    plan = {
                        'id' : cart_ids[i],
                        'quantity': $(pq).value
                   }
                   planQuantities.push(JSON.encode(plan) + '|'); /* used for serverside parsing later */
                }
                m.checkout();
            });
        }

        /* Activates 'proceed checkout' button upon agreeing to terms and condition*/

        if ($(self.termsAndConditionId)) {
            $(self.termsAndConditionId).removeEvents();
            $(self.termsAndConditionId).addEvent('click', function(e){
                if($(self.termsAndConditionId).checked) {
                    $(self.procedeCheckoutErrorId).setStyle('display', 'none')
                    // $(self.procedeCheckoutId).set('disabled', false);
                }
                else {
                    // $(self.procedeCheckoutId).set('disabled', true);
                }
            });
        }

        /* Shows error message when user clicked proceed to payment without agreeing to terms */

        if ($(self.procedeCheckoutId)) {
            $(self.procedeCheckoutId).removeEvents();
            $(self.procedeCheckoutId).addEvent('click', function(e){
                if($(self.termsAndConditionId).checked) {
                }
                else {
                    e.preventDefault();

                    var unchecked_err_message = 'Please read and agree to the Terms and Conditions before proceeding to checkout.'
                    $(self.procedeCheckoutErrorId).getElement('p.notification-message').set('text', unchecked_err_message)

                    $(self.procedeCheckoutErrorId).setStyle('display', 'block')
                }
            });
        }

        /* opens new window for complete terms and condition */

        if ($(self.termsAndConditionLinkId)) {
            $(self.termsAndConditionLinkId).removeEvents();
            $(self.termsAndConditionLinkId).addEvent('click', function(e){
                window.open('/terms-conditions', '_blank')
            });
        }

        /** toggles the payment options in purchase package page
         *
         */
        $$(".com-purchase-package .expand-tutorial-lnk").addEvent('click', function(event) {
            event.preventDefault();
            $$(".com-purchase-package .payment-options").toggleClass("active");
        });


        /**
            DISMISS LINKS
        */

        if($$(".dismiss")) {
            $$(".dismiss").addEvent("click", function(e){
                if ($$(".com-tutorial-smart-payment")) {
                    $$(".com-tutorial-smart-payment").setStyle("display", "none");
                    $("overlay").setStyle("display", "none");
                }
                if ($$(".com-tutorial-dragonpay")) {
                    $$(".com-tutorial-dragonpay").setStyle("display", "none");
                    $("overlay").setStyle("display", "none");
                }
            });
        }

        /**
            TUTORIAL
        */
        if ($("tutorial-payment-smart")) {
            $("tutorial-payment-smart").addEvent("click", function(e){
                e.preventDefault();
                $$(".com-tutorial-smart-payment")[0].show();
                $$("#overlay").show();

            });

        }


        if ($("tutorial-payment-dragonpay")) {
            $("tutorial-payment-dragonpay").addEvent("click", function(e){
                e.preventDefault();
                $$(".com-tutorial-dragonpay")[0].show();
                $$("#overlay").show();

            });
        }


        $$('.info-item.info-item-paypal a.info-lnk').addEvent("click", function(e){
            e.preventDefault();
            $$('.com-tutorial-paypal.com-003v.ui-dialog').show();
            $$("#overlay").show();

        });


        // PAYMAYA
        $$('.info-item.info-item-paymaya a.info-lnk').addEvent("click", function(e){
            e.preventDefault();
            $$('.com-tutorial-paymaya.com-003v.ui-dialog').show();
            $$("#overlay").show();

        });



    };

    /**
        On change Events
    **/

    this.onChange = function() {

        /* updates total cost when quantity is changed */

        $$('input[id^=' + self.planQuantityId + ']').removeEvents();

        $$('input[id^=' + self.planQuantityId + ']').addEvent('focus', function(e){
            self.lastPrice = parseInt($(this.getParent('tr').getElementById(self.totalId)).get('text').substring(1));
        })

        $$('input[id^=' + self.planQuantityId + ']').addEvent('keyup', function (e){
            e.preventDefault();

            if (this.value == '0'){
                this.value = '1';
            }


            if (!intRegex.test(this.value)) {
                if (intRegex.test($(this.getParent('tr').getElementById(self.totalId)).get('text').substring(1))){
                    self.lastPrice = parseInt($(this.getParent('tr').getElementById(self.totalId)).get('text').substring(1));
                }
                self.isLastPriceInt = false;
                $(this.getParent('tr').getElementById(self.totalId)).set('html', '<font color="red">Invalid quantity.</font>');
                $(this.getParent('tr').getElement('input[type=text]')).setStyle('border', '1px solid red');
                $('checkout').disabled = true;
            }
            else {
                $(this.getParent('tr').getElement('input[type=text]')).setStyle('border', '1px solid #B0B6C1');
                if (self.isLastPriceInt || !self.lastPrice) {
                    self.lastPrice = parseInt($(this.getParent('tr').getElementById(self.totalId)).get('text').substring(1));
                }
                newPrice = parseInt(this.value) * parseInt($(this.getParent('tr').getElementById(self.amountPerQuantity)).value);
                $(this.getParent('tr').getElementById(self.totalId)).set('html', 'P' + newPrice);

                lastTotalPrice = parseInt($(totalCostId).get('text').substring(1));
                newPriceTotal = lastTotalPrice + newPrice - self.lastPrice;
                $(totalCostId).set('html', 'P' + newPriceTotal);

                self.isLastPriceInt = true;
                $('checkout').disabled = false;


                // to toggle display of balance threshold notification
                if (  parseInt( newPriceTotal )+ parseInt($('current_balance').value)     > $('balance_threshold').value ){
                    $$('.notification').hide()
                }
                else{
                    $$('.notification').show()
                }


                //console.log('new price '+newPriceTotal+ 'versus '+$('current_balance').value)
            }
        });
    };

    /**
        Adds all defined events
    **/
    for(ev in this)
        this[ev]();
}

/**
    Activates all JS scripts
**/

window.addEvent('domready', function(){
    var c = new ControllersShoppingCart();
});
