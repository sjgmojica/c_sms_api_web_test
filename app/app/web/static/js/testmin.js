/**
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - contains frontend implementations 
        for enrolling testmin, testing MO and MT messages
**/

/**
    Views (for rendering dynamic ajax templates)
**/

var ViewsTestmin = { 
    
    /* renders pincode dialog box dynamically for testmin enrollment (used after ajax call to render pop up) */
    
    renderPincodeDialog : function(response) {
        
        html =     '<div class="com-pin-code-cr">'
            + '        <header>'
            + '            <h1 class="at">PIN Code</h1>'
            + '            <p class="txt-ttl">PIN Code</p>'
            + '            <!-- Dismiss link -->'
            + '<p class="dismiss-link-cr"><a id="dismiss_dialog" class="dismiss-link" href="#"><span class="lbl">Dismiss</span></a></p>        </header>'
            + '        <div class="com-pin-code-ct">'
            + '            <form class="com-pin-code-frm">'
            + '                <fieldset>'
            + '                    <legend>PIN Code</legend>'
            + '                    <p class="txt-desc">Enter the PIN Code we sent you.</p>';
            
            if(response.error) {
                html += '                    <!-- Notification (error) -->'
                    + '<div id="pincode_notification_error" class="notification notification-error">'
                    + '	<p id="pincode_notification_message" class="notification-message">' + response.response + '</p>'
                    + '</div>';
            }
            if(response.error_captcha != null) {
            
                html += '                    <!-- Notification (error) -->'
                    + '<div id="pincode_notification_error" class="notification notification-error">'
                    + '	<p id="pincode_notification_message" class="notification-message">' + response.error_captcha + '</p>'
                    + '</div>';
            }
            if (!response.error && !('error_captcha' in response) && response.response) {   
                
                html +=  '<!-- Notification (success) -->'
                    + '<div pincode_notification_error class="notification notification-success">'
                    +    '<p pincode_notification_message class="notification-message">' + response.response + '</p>'
                    + '</div>';             
            }
            
            if(!response.hide_pincode_box) {
                
                /* captcha */
                if (response.captcha || response.captcha == "true" || response.captcha == 'True') {
                    /*
                    html += '<header>'
                        '<h1 class="at">Prove you\'re human</h1>'
                            '<p class="txt-ttl">Prove you\'re human</p>'
                        '</header>';
                    html += "<fieldset><p class='txt-desc'>You need to pass this Captcha test to continue</p></fieldset>";
                    */
                    html += "Prove you're human <br/>"
                        + "You need to pass this Captcha test to continue";
                }
                
                html += ' <div id="captchadiv"></div>';
           
                /* pincode */
                html +='                    <div class="fld fld-txt fld-pin">'
                    + '                        <div class="psu-inp psu-inp-txt pus-inp-pin">'
                    + '                            <label>PIN Code</label>'                
                    + '         <input id="code" name="code" class="inp-pin" type="text" placeholder="PIN Code" required>';
            }

            html += '            <input id="testmin" name="testmin" type="hidden" value="' + response.testmin +'"/>'
                + '            <input id="max_code_request" name="max_code_request" type="hidden" value="' + response.max_code_request + '"/>'
                + '            <input id="ver_id" name="ver_id" type="hidden" value="' + response.ver_id + '"/>';
            
            /* displays recaptcha when needed */
            
            if (!response.max_code_request || response.max_code_request == "false") {
                    html += '<p class="resend-pin-lnk-cr"><a id="resend_link" class="resend-pin-lnk" href="' + response.ver_id + '"><span class="lbl">Resend PIN Code</span></a></p>';
            }         
            
            html += '                        </div>'
                + '                    </div>'
                + '                    <div class="fld fld-axn">';

            if(!response.hide_pincode_box) {
        
                html += '                        <div class="psu-btn psu-btn-pri psu-btn-sub">'
                    + '                            <button id="min_pincode_submit" class="btn-sub" type="submit">Submit</button>'
                    + '                        </div>';
            }
                
                html += '                        <div class="psu-btn psu-btn-neg psu-btn-cncl">'
                    + '                            <a id="dismiss_dialog" class="cncl-lnk" href="#"><span class="lbl">Cancel</span></a>'
                    + '                        </div>';
                
            if(!response.hide_code_pinbox) {
                html += '                    </div><!--.fld-axn-->'
                    +  '</fieldset>';

            }
            
            html += '          </form>'
                    + '       </div>'
                    + '   </div>';
                                           
            if (mo_flag) {
                 $("mo_dialog").set('html', html);
                 $("mo_dialog").setStyle('display', 'block');            
            }
            else {
                $("ui_dialog").set('html', html);
                $("ui_dialog").setStyle('display', 'block');   
            }
            
            $('overlay').setStyle('display', 'block');
            
            if (response.captcha || response.captcha == "true" || response.captcha == 'True') {
                window.addEvent("domready", function(){
                    renderRecaptcha();
                });
            }  
    
        var testminC = new ControllersTestmin(); /* adds events to ajax calls @todo: REVISE THIS. */
        var commonC = new Controller(); /* adds events to ajax calls @todo: REVISE THIS. */                     
    }  
}


/**
    MODEL (for ajax calls)
**/

var ModelsTestmin = function() {  
    
    /**
        Variable Definitions
    **/
    
        
    self.moNotificationSuccessId = 'mo_notification_success';
    self.moNotificationSuccessMessageId = 'mo_notification_success_message';
    self.moNotificationErrorId = 'mo_notification_error';
    self.moNotificationErrorMessageId = 'mo_notification_error_message';
    self.testminMessageId2 = 'testmin_message2';
    
    /**
        Ajax Functions Definitions
    **/
    
    this.verifyTestmin = function (onSuccess){
        
        // debug
        
        // debug
        
        /*  verify enrolled min */
        
        new Request.JSON(
        {    
            'url' : '/testmin/enroll/submit',
            'method' : 'POST',
            'data' : {      
                'testmin': testmin
            },
            'onSuccess' : function(response)
            {   
                if(response.error){
                    $$('p[id="notification_message"]').set('text', response.response);
                    $$('div[id="notification_error"]').setStyle('display', 'block');
                }
                else {
                    onSuccess(response);
                }
            }
        }).send();        
    }
        
      
    this.resendPincode = function (onSuccess){
        
        /* resends pincode */
    
        new Request.JSON(
        {    
            'url' : '/testmin/resendcode',
            'method' : 'GET',
            'data' : {      
                'ver_id': ver_id
            },
            'onSuccess' : function(response)
            {   
                onSuccess(response)
            }
        }).send();        
    }   
       
    this.verifyTestminPincode = function (onSuccess){
        
        /* verifies pincode */
    
        new Request.JSON(
        {    
            'url' : '/testmin/verify',
            'method' : 'POST',
            'data' : {     
                'code': code,
                'testmin': testmin,
                'max_code_request': max_code_request,
                'ver_id': ver_id,
                'recaptcha_challenge_field': recaptcha_challenge_field,
                'recaptcha_response_field': recaptcha_response_field
            },
            'onSuccess' : function(response)
            {   
                if(!response.error && !('error_captcha' in response)) {
                // if(!response.error && response.error_captcha == null) {
                    onSuccess(response);
                    setTimeout('window.location.href="/testmin/enroll"', 1000);
                }
                else {
                    onSuccess(response);
                }
            }
        }).send();        
    }
    
    this.saveMo = function (new_mo_message){
        new Request.JSON(
        {    
            'url' : '/testmo/save',
            'method' : 'POST',
            'data' : {      
                'MO_message': mo_message
            },
            'onSuccess' : function(response)
            {   
                if(response.error) {
                    $(self.moNotificationErrorMessageId).set('text', response.message);
                    $(self.moNotificationErrorId).setStyle('display', 'block');
                }
                else {
                    $(self.moNotificationSuccessMessageId).set('text', response.message);
                    $(self.moNotificationSuccessId).setStyle('display', 'block');
                    $(self.testminMessageId2).set('placeholder', new_mo_message); 
                }
            }
        }).send();        
    }   

}


/**
    Controller (for events)
**/

var ControllersTestmin = function () { 
 
    var m = new ModelsTestmin(),
        v = ViewsTestmin;
        
    /**
        Variable Definitions
    **/
    
    /* enrollment */
    
    self.editMinMtId = 'edit_min_mt';
    self.savedMinMoId = 'saved-min-mo';
    self.savedMinMtId = 'saved-min-mt';
    self.editMinClassMtId = 'edit_min_class_mt';
    self.editMinMoId = 'edit_min_mo';
    self.editMinClassMoId = 'edit_min_class_mo';
    self.verifyMinMtId = 'verify_min_mt';
    self.verifyMinMoId = 'verify_min_mo';
    self.testminId = 'testmin';
    self.testminMtId = 'testmin_mt';
    self.testminMoId = 'testmin_mo';
    self.tabMinId1 = 'tab_min1';
    self.tabMinId2 = 'tab_min2';
    self.sendTabId = 'send_tab';
    self.receiveTabId = 'receive_tab';
    self.sendTabSectionId = 'send_tab_section';
    self.receiveTabSectionId = 'receive_tab_section';
    self.codeBoxId = 'code';
    
    self.minPincodeSubmitId = 'min_pincode_submit';
    self.resendLinkId = 'resend_link';
    
    /* MT MO */
    
    self.saveMoReplyId = 'save_mo_reply';
    self.testminMessageId1 = 'testmin_message1';
    self.testminMessageId2 = 'testmin_message2';
    self.testminCharCountId1 = 'testmin_char_count1';
    self.testminCharCountId2 = 'testmin_char_count2';
    self.testminCharCtr1 = 118;
    self.testminCharCtr2 = 118;
    self.testminMaxChar = 118;
    
    /**
        Onclick events
    **/
    
    this.onClick = function () {
        
        /* dismiss dialogs */
        $$("a[id='dismiss']").addEvent('click', function(e) {
            if ($$(".com-tutorial-send-message") != null) {
                $$(".com-tutorial-send-message").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }
            if ($$(".com-tutorial-enroll-number") != null) {
                $$(".com-tutorial-enroll-number").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }
            if ($$(".com-tutorial-receive-message") != null) {
                $$(".com-tutorial-receive-message").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }
        });
       
        $$(".skip-lnk").addEvent('click', function(e) {
            if ($$(".com-tutorial-send-message") != null) {
                $$(".com-tutorial-send-message").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }    
            if ($$(".com-tutorial-enroll-number") != null) {
                $$(".com-tutorial-enroll-number").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }
            if ($$(".com-tutorial-receive-message") != null) {
                $$(".com-tutorial-receive-message").setStyle('display', 'none');
                $('overlay').setStyle('display', 'none');
            }
        });
               
        
        if ($(self.testminMessageId1)) {
            $$('p[id=' + self.testminCharCountId1 + ']').set('html', self.testminMaxChar - $(self.testminMessageId1).value.length);
            $$('p[id=' + self.testminCharCountId2 + ']').set('html', self.testminMaxChar - $(self.testminMessageId2).value.length);
        }
         
        if ($$('div[id=' + self.editMinClassMtId + ']') != null) {
            $$('div[id=' + self.editMinClassMtId + ']').setStyle('display', 'block');
        }
        
        /*
        if($(self.editMinMtId) != null){
            $$('a[id=' + self.editMinMtId + ']').removeEvents();
            $$('a[id=' + self.editMinMtId + ']').addEvent('click', function(e){
                e.preventDefault();
                $$('div[id=' + self.editMinClassMtId + ']').setStyle('display', 'block');
                $$('div[id=' + self.editMinClassMoId + ']').setStyle('display', 'none');
                $$('div[id=' + self.savedMinMtId + ']').setStyle('display', 'none');
                $$('div[id=' + self.savedMinMoId + ']').setStyle('display', 'block');
            });
        }
        */
        
        if($(self.verifyMinMtId) != null){
            $$('button[id=' + self.verifyMinMtId + ']').removeEvents();
            $$('button[id=' + self.verifyMinMtId + ']').addEvent('click', function(e){
                e.preventDefault();
                testmin = $(self.testminMtId).value;
                mo_flag = false;
                m.verifyTestmin(v.renderPincodeDialog);
            });
        }
        
        if($(self.editMinMoId) != null){
            $$('a[id=' + self.editMinMoId + ']').removeEvents();
            $$('a[id=' + self.editMinMoId + ']').addEvent('click', function(e){
                e.preventDefault();
                $$('div[id=' + self.editMinClassMoId + ']').setStyle('display', 'block');
                $$('div[id=' + self.editMinClassMtId + ']').setStyle('display', 'none');
                $$('div[id=' + self.savedMinMoId + ']').setStyle('display', 'none');
                $$('div[id=' + self.savedMinMtId + ']').setStyle('display', 'block');
            });
        }
        
        if($(self.verifyMinMoId) != null){
            $$('button[id=' + self.verifyMinMoId + ']').removeEvents();
            $$('button[id=' + self.verifyMinMoId + ']').addEvent('click', function(e){
                e.preventDefault();
                testmin = $(self.testminMoId).value;
                mo_flag = true;
                m.verifyTestmin(v.renderPincodeDialog);
            });
        }
        
        /* toggle class (for selecting between test MT and MO tab) */
                
        if($(self.tabMinId1) != null){
            $$('li[id=' + self.tabMinId1 + ']').removeEvents();
            $$('li[id=' + self.tabMinId1 + ']').addEvent('click', function(e){
                e.preventDefault();
                $(self.tabMinId1).toggleClass('active');
                $(self.tabMinId2).toggleClass('active');
                $(self.sendTabSectionId).toggleClass('active');
                $(self.receiveTabSectionId).toggleClass('active');
            });
            
            $$('li[id=' + self.tabMinId2 + ']').removeEvents();
            $$('li[id=' + self.tabMinId2+ ']').addEvent('click', function(e){
                e.preventDefault();
                $(self.tabMinId1).toggleClass('active');
                $(self.tabMinId2).toggleClass('active');
                $(self.sendTabSectionId).toggleClass('active');
                $(self.receiveTabSectionId).toggleClass('active');
            });
        }
        
        /* pincode verification */
        
        if($(self.minPincodeSubmitId) != null){
            $$('button[id=' + self.minPincodeSubmitId + ']').removeEvents();
            $$('button[id=' + self.minPincodeSubmitId + ']').addEvent('click', function(e){
                e.preventDefault();
                code = $('code').value;
                
                if ($('testmin_mt') != null && $('testmin_mt').value != '') {
                    testmin = $('testmin_mt').value;
                }
                else if ($('testmin_mo') != null && $('testmin_mo').value != '') {
                    testmin = $('testmin_mo').value;
                }
                else {
                    testmin = $('testmin').value;
                }
                max_code_request = $('max_code_request').value;
                ver_id = $('ver_id').value;
                
                recaptcha_challenge_field = null;
                recaptcha_response_field = null;
                
                if ($('recaptcha_challenge_field') != null) {
                    recaptcha_challenge_field = $('recaptcha_challenge_field').value;
                    recaptcha_response_field = $('recaptcha_response_field').value;
                }
                m.verifyTestminPincode(v.renderPincodeDialog);
            });
        }
        
        /* resend pincode */
           
        if($(self.resendLinkId) != null){
            $$('a[id=' + self.resendLinkId + ']').removeEvents();
            $$('a[id=' + self.resendLinkId + ']').addEvent('click', function(e){
                e.preventDefault();
                ver_id = this.get('href')
                m.resendPincode(v.renderPincodeDialog);
            });
        }
        
        /* shows verify button */
        
        if ( $$('#saved-min-mt a.dismiss-link')[0]  ) {
            $$('#saved-min-mt a.dismiss-link')[0].addEvent('click', function(event) {
            event.preventDefault();
            $("saved-min-mt").removeClass("active");
            $("com-verify-number-cr").addClass("active");
        });

        }       
 
        if ($("cancel-new-mobile")) {
        $("cancel-new-mobile").addEvent('click', function(event) {
            event.preventDefault();
            $("saved-min-mt").addClass("active");
            $("com-verify-number-cr").removeClass("active");
        });
	}
        /**
            TUTORIALS
        */
        
        if ($("tutorial-receive-message")) {
            $("tutorial-receive-message").removeEvents();
            $("tutorial-receive-message").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-receive-message")[0].show();
                $$("#overlay").show();
            });
        }
        
 
    }
    
    this.onKeyStroke = function() {
        
        if($(self.codeBoxId) != null){
            $(self.codeBoxId).removeEvents();
            $(self.codeBoxId).addEvent('keydown', function(e) {
         
                if(e.key == 'enter') {
                    e.stop();
                    code = $('code').value;
                    
                    if ($('testmin_mt') != null && $('testmin_mt').value != '') {
                        testmin = $('testmin_mt').value;
                    }
                    else if ($('testmin_mo') != null && $('testmin_mo').value != '') {
                        testmin = $('testmin_mo').value;
                    }
                    else {
                        testmin = $('testmin').value;
                    }
                    max_code_request = $('max_code_request').value;
                    ver_id = $('ver_id').value;
                    
                    recaptcha_challenge_field = null;
                    recaptcha_response_field = null;
                    
                    if ($('recaptcha_challenge_field') != null) {
                        recaptcha_challenge_field = $('recaptcha_challenge_field').value;
                        recaptcha_response_field = $('recaptcha_response_field').value;
                    }
                    m.verifyTestminPincode(v.renderPincodeDialog);
                }
            });
        }
    };
    
    /**
        onChange events
    **/
    
    this.onChange = function() {
        
       /* save mo reply */
       
       if ($(self.saveMoReplyId)) {
            $(self.saveMoReplyId).removeEvents();
            $(self.saveMoReplyId).addEvent('click', function(e) {
                e.preventDefault();
                mo_message = $(self.testminMessageId2).value;
                m.saveMo(mo_message);
            });
       }
        
        /* 
            Updates char count for every type 
            @todo: case when user do not release key down 
            (i.e. will result to ddddddddddddd) 
        */
        
        if ($(self.testminMessageId1)) {
            $$('textarea[id=' + self.testminMessageId1 + ']').removeEvents();
            $$('textarea[id=' + self.testminMessageId1 + ']').addEvent('keyup', function(e){
                
                /*
                keyId = e.key;
                switch(keyId) {
                    case 'backspace':
                        if (testminCharCtr1 < testminMaxChar)
                            self.testminCharCtr1++;
                        break;
                    case 'delete':
                        if (testminCharCtr1 < testminMaxChar)
                            self.testminCharCtr1++;
                        break;
                    default:
                        if (testminCharCtr1 > 0)
                            self.testminCharCtr1--;
                        break;
                }
                */
                
                $$('p[id=' + self.testminCharCountId1 + ']').set('html', self.testminMaxChar - this.value.length);
            });
            
            $$('textarea[id=' + self.testminMessageId2 + ']').removeEvents();
            $$('textarea[id=' + self.testminMessageId2 + ']').addEvent('keyup', function(e){
                
                /*
                keyId = e.key;
                switch(keyId) {
                    case 'backspace':
                        if (testminCharCtr2 < testminMaxChar)
                            self.testminCharCtr2++;
                        break;
                    case 'delete':
                        if (testminCharCtr2 < testminMaxChar)
                            self.testminCharCtr2++;
                        break;
                    default:
                        if (testminCharCtr2 > 0)
                            self.testminCharCtr2--;
                        break;
                }
                */
                
                $$('p[id=' + self.testminCharCountId2 + ']').set('html', self.testminMaxChar - this.value.length);
            });
        }
    }
    
    /**
        Activates all events
    **/
    for(ev in this)
        this[ev]();
}

window.addEvent('domready', function(){ 
    var testmin = new ControllersTestmin();
});
