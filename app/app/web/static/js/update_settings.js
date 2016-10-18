/**
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - contains frontend implementations 
        for updating account and API settings processes.
**/

/**
    Views (for rendering dynamic ajax templates)
**/

var ViewsSettings = {

}


/**
    MODEL (for ajax calls)
**/

var ModelsSettings = function() {  
    
    /**
        Variable Definitions
    **/
    
    self.publicKeyErrorId = 'public_key_error';
    self.callbackUrlErrorId = 'callback_url_error';
    self.moUrlErrorId = 'mo_url_error';
    self.verifyPublicKeyErrorId = 'verify_public_key_error';
    self.verifyPublicKeySuccessId = 'verify_public_key_success';
    
    /**
        Ajax Functions Definitions
    **/
    
        /* api settings -> edit */
    
    this.apiSettingsEdit = function (onSuccess){
    
        // $(self.publicKeyErrorId).set('text', '');
        $(self.callbackUrlErrorId).set('text', '');
        $(self.moUrlErrorId).set('text', '');
        
        new Request.JSON(
        {    
            'url' : '/api/settings',
            'method' : 'POST',
            'data' : {      
                // 'public_key': public_key,
                'callback_url': callback_url,
                'mo_url': mo_url
            },
            'onSuccess' : function(response)
            {   
                if (!response.has_error){
                    window.location = '/api/settings/' + 'success';
                    // $('notif_success').set('text', response.success_message);
                    // $('notification-success').setStyle('display', 'block');
                }
                else {
                    // if(response.errors.public_key) {
                        // $(self.publicKeyErrorId).set('text', response.errors.public_key);
                    // }
                    if(response.errors.callback_url) {
                        $(self.callbackUrlErrorId).set('text', response.errors.callback_url);
                    }
                    if(response.errors.mo_url) {
                        $(self.moUrlErrorId).set('text', response.errors.mo_url);
                    }
                }
            }
        }).send();        
    }
       
    /* api settings -> verify public key */
    
    this.verifyPublicKey = function (onSuccess){
        new Request.JSON(
        {    
            'url' : '/api/settings/publickey/verify',
            'method' : 'POST',
            'data' : {      
                'rsa_message': rsa_message,
                'rsa_signature': rsa_signature
            },
            'onSuccess' : function(response)
            {   
                if(response.error && response.error != "false") {
                    $(self.verifyPublicKeyErrorId).set('text', response.message);
                    $(self.verifyPublicKeyErrorId).setStyle('display', 'block');
                }
                 else {
                    $(self.verifyPublicKeyErrorId).setStyle('display', 'none');
                    $(self.verifyPublicKeySuccessId).set('text', response.message);
                    $(self.verifyPublicKeySuccessId).setStyle('display', 'block');
                    setTimeout('window.location.href="/api/settings"', 1000);
                }
            }
        }).send();        
    }
        
    /* account settings -> update */
    
    this.updateAccountSettings = function(onSuccess) {
        new Request.JSON(
        {    
            'url' : '/account/settings/change',
            'method' : 'POST',
            'data' : {      
                'firstname': firstname,
                'lastname': lastname,
                'company': company,
                'address': address
            },
            'onSuccess' : function(response)
            {   
                window.location = '/account/settings/view/' + response.message;
            }
        }).send(); 
    }   
}


/**
    Controller (for events)
**/

var ControllersSettings = function () {
    
    var m = new ModelsSettings(),
        v = ViewsSettings;
   
    self.uiDialogId = 'ui_dialog';
    
    /* api settings */
    
    self.apiEditIconId = 'api_edit_icon';
    self.apiSettingsSaveId = 'api_settings_save';
    
    self.apiPublicKeyId = 'public_key';
    self.apiCallbackUrlId = 'callback_url';
    self.apiMoUrlId = 'mo_url';
    
    self.verifyPublicKeyId = 'verify_public_key';
    self.verifyPublicKeyDialogId = 'verify_public_key_dialog';
    self.verifyPublicKeySubmitId = 'verify_public_key_submit';
    self.rsaMessageId = 'rsa_message';
    self.rsaSignatureId = 'rsa_signature';

     /* account settings */
    
    self.editSettingsId = 'edit_settings';
    self.editEmailSettingsId = 'edit_email_settings';
    self.editPasswordSettingsId = 'edit_password_settings';
    
    self.editNameAddressId = 'edit_name_address';
    self.editEmailId = 'edit_email';
    self.editPasswordId = 'edit_password';
    self.acccountSettingsDismissDialogId = 'settings_dismiss_dialog';
    
    self.apiSettingsDismissDialogId = 'api_settings_dismiss_dialog';
    
    self.submitAccountSettingsId = 'submit_account_settings';
    self.firstNameId = 'first_name';
    self.lastNameId = 'last_name';
    self.companyId = 'company';
    self.addressId = 'address';
   
    self.generalNotifId = 'general_notif';
    self.generalNotifErrorId = 'general_notif_error';
    self.firstNameInlineNotifId = 'first_name_notif';
    self.lastNameInlineNotifId = 'last_name_notif';
    self.companyInlineNotifId = 'company_notif';
    self.addressInlineNotifId = 'address_notif';
    
    
    /**
        onClick Events
    **/
    
    this.onClick = function () {
       
        /* account settings */
        
        if($(self.submitAccountSettingsId) != null){
            $(self.submitAccountSettingsId).removeEvents();
            $(self.submitAccountSettingsId).addEvent('click', function(e){
                e.preventDefault();
                error = false;
                
                /* input validation, renders individual inline error notifs */
                
                firstname = '';
                lastname = '';
                company = '';
                address = '';
                
                $(self.generalNotifId).set('text', '');
                $(self.generalNotifErrorId).setStyle('display', 'none');
                $(self.firstNameInlineNotifId).set('text', '');
                $(self.lastNameInlineNotifId).set('text', '');
                $(self.addressInlineNotifId).set('text', '');
                
                errorCtr = 0; /* will be used in determining when all required fields are not passed */
                
                if($(self.firstNameId).value == '') {
                    error = true;
                    errorCtr++;
                    $(self.firstNameInlineNotifId).set('text', "You can't leave this empty.");
                }
                else {
                    firstname = $(self.firstNameId).value;
                    $(self.firstNameInlineNotifId).set('text', '');
                }
                if($(self.lastNameId).value == '') {
                    error = true;
                    errorCtr++;
                    $(self.lastNameInlineNotifId).set('text', "You can't leave this empty.");
                }
                else {
                    lastname = $(self.lastNameId).value;
                    $(self.lastNameInlineNotifId).set('text', '');
                }
                if($(self.addressId).value == ''){
                    error = true;
                    errorCtr++;
                    $(self.addressInlineNotifId).set('text', "You can't leave this empty.");
                }
                else {
                    address = $(self.addressId).value;
                    $(self.addressInlineNotifId).set('text', '');
                } 
                if(!$(self.companyId).value == ''){   
                    company = $(self.companyId).value;
                }
                if (errorCtr == 3) {
                    /* show general error instead of seperate ones */
                    $(self.generalNotifId).set('text', 'Please complete your account information below.');
                    $(self.generalNotifErrorId).setStyle('display', 'block');
                    
                    /* resets all separate errors */                    
                    $(self.firstNameInlineNotifId).set('text', '');
                    $(self.lastNameInlineNotifId).set('text', '');
                    $(self.addressInlineNotifId).set('text', '');
                }
                
                else if (!error){
                    m.updateAccountSettings();
                }
            });
        }
        
         if( $(self.editSettingsId)) {
            $$('a[id=' + self.editSettingsId + ']').removeEvents();
            $$('a[id=' + self.editSettingsId + ']').addEvent("click", function (e){
                e.preventDefault();
                $(self.editNameAddressId).setStyle('display', 'block');
                $(self.overlayId).setStyle('display', 'block');
            });
        }
        
        /* email */
        
        $$('a[id=' + self.editEmailSettingsId + ']').removeEvents();
        $$('a[id=' + self.editEmailSettingsId + ']').addEvent("click", function (e){
            e.preventDefault();
            $(self.editEmailId).setStyle('display', 'block');
            $(self.overlayId).setStyle('display', 'block');
        });
           
        /* password */
        
        $$('a[id=' + self.editPasswordSettingsId + ']').removeEvents();
        $$('a[id=' + self.editPasswordSettingsId + ']').addEvent("click", function (e){
            e.preventDefault();
            $(self.editPasswordId).setStyle('display', 'block');
            $(self.overlayId).setStyle('display', 'block');
        });

//        if ($(self.acccountSettingsDismissDialogId) != null){
//            $$('a[id=' + self.acccountSettingsDismissDialogId + ']').removeEvents();
//            $$('a[id=' + self.acccountSettingsDismissDialogId + ']').addEvent('click', function(e){
//                $(self.editNameAddressId).setStyle('display', 'none');
//                $(self.overlayId).setStyle('display', 'none');
//                
//                if($(self.editPasswordId) != null)
//                    $(self.editPasswordId).setStyle('display', 'none');
//                if($(self.editEmailId) != null)
//                    $(self.editEmailId).setStyle('display', 'none');
//            });
//        }
        
        /* api settings */
        
        if($(self.apiEditIconId) != null){
            $(self.apiEditIconId).removeEvents();
            $(self.apiEditIconId).addEvent('click', function(e){
                e.preventDefault();
                $(self.uiDialogId).setStyle('display', 'block');
                $(self.overlayId).setStyle('display', 'block');
            });
        }
       
        /* api settings -> edit */
        
        if($(self.apiSettingsSaveId) != null){
            $(self.apiSettingsSaveId).removeEvents();
            $(self.apiSettingsSaveId).addEvent('click', function(e){
                e.preventDefault();
               
                // public_key = $(self.apiPublicKeyId).value;
                callback_url = $(self.apiCallbackUrlId).value;
                mo_url = $(self.apiMoUrlId).value;
                
                m.apiSettingsEdit();
            });
        } 
        
        /* api settings -> show verify public key dialog */
                    
        if($(self.verifyPublicKeyId) != null){
            $(self.verifyPublicKeyId).removeEvents();
            $(self.verifyPublicKeyId).addEvent('click', function(e){
                e.preventDefault();
                $(self.verifyPublicKeyDialogId).setStyle('display', 'block');
                $(self.overlayId).setStyle('display', 'block');
            });
        } 
        
        /* api settings -> verify public key -> submit */
                    
        if($(self.verifyPublicKeySubmitId) != null){
            $(self.verifyPublicKeySubmitId).removeEvents();
            $(self.verifyPublicKeySubmitId).addEvent('click', function(e){
                e.preventDefault();
                rsa_message = $(self.rsaMessageId).get('text');
                rsa_signature = $(self.rsaSignatureId).value;
                
                m.verifyPublicKey();
            });
        } 
        
        /* api dismiss dialogs */
        
        if ($(self.apiSettingsDismissDialogId) != null){
            $$('a[id=' + self.apiSettingsDismissDialogId + ']').removeEvents();
            $$('a[id=' + self.apiSettingsDismissDialogId + ']').addEvent('click', function(e){
                e.preventDefault();
                if ($(self.verifyPublicKeyDialogId)) {
                    $(self.verifyPublicKeyDialogId).setStyle('display', 'none');
                }
                if ($(self.uiDialogId)) {
                    $(self.uiDialogId).setStyle('display', 'none');
                }
                if ($(self.overlayId)) {
                    $(self.overlayId).setStyle('display', 'none');
                }
                if ($$(".com-tutorial-api-settings")) {
                    $$(".com-tutorial-api-settings").setStyle("display", "none");
                }
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
    var settingsC = new ControllersSettings();
});
