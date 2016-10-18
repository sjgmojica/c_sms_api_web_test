/**
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - contains frontend implementations 
        for common chikka sms api processes.
**/

var Views = function() {

}

var Model = function (){

}

var Controller = function (){
    
    self.dismissDialogId = 'dismiss_dialog';
    self.uiDialogId = 'ui_dialog';
    self.moDialogId = 'mo_dialog';
    self.editPasswordId = 'edit_password';
    self.overlayId = 'overlay';
    self.notificationId = 'notification_message';
    self.notificationBlockId = 'notification';
    
    self.helpTabId = 'nav-menu-help';                
    self.docsTabId = 'nav-menu-docs';                
    
    self.bodyId = 'body';
    self.navMenuLogsId = '.nav-menu-logs';
    self.navMenuSettId = '.nav-menu-sett';
                   
    this.onClick = function (){
              
        if ($(self.dismissDialogId) != null){
            $$('a[id=' + self.dismissDialogId + ']').removeEvents();
            $$('a[id=' + self.dismissDialogId + ']').addEvent('click', function(e){
                $$('div[id=' + self.uiDialogId + ']').setStyle('display', 'none');
                $(self.overlayId).setStyle('display', 'none');
                if ($(self.moDialogId) != null) {
                    $(self.moDialogId).setStyle('display', 'none');
                }
                if ($(self.verifyPublicKeyDialogId) != null) {
                    $(self.verifyPublicKeyDialogId).setStyle('display', 'none');
                }
                if ($(self.self.editPasswordId) != null) {
                    $(self.self.editPasswordId).setStyle('display', 'none');
                }
            });
        }

        /* closes drop down when user clicks outside */
      
        if ($$(self.bodyId)) {
            $$(self.bodyId).removeEvents();
            $$(self.bodyId).addEvent('click', function(e) {
                if(e.target.className!='') {
                    $$(self.navMenuLogsId).removeClass('selected');
                    $$(self.navMenuSettId).removeClass('selected');
                }
           	});
        }
        

       
    }  
    
    this.onChange = function() {
        
    };
    
    this.onSelect = function (){
        
    };
    
     this.onScroll = function () {

        /* BACK TO TOP */
        
        if ($$('.back-top-link-cr') != null) {
            $(window).addEvent('scroll', function(e) {
                if ($(this).getScroll().y > 210) {
                    $$('.back-top-link-cr').reveal();
                } else {
                    $$('.back-top-link-cr').dissolve();
                }
            });
            $$('.back-top-link-cr a').addEvent('click', function(event) {
                new Fx.Scroll(window).start(0, 200);
                return false;
            });
        }            
    };
        
    for(ev in this)
        this[ev]();
};

var Utils = {
    sendGoogleAnalytics : function(gaObj){
        /**
        * Sructure of object to be passed
        * var gaObj = {
        *   'category' : 'Sign in',
        *   'action' : 'Signed in using Mobile Number',
        *   'label' : 'Sign in'
        *  };
        *
        **/
        
        ga('send', 'event', gaObj['category'], gaObj['action'], gaObj['label']);
    }
}


// sets dynamic body height 

function setFooter(){
    /*
     * adjusts the body height so the footer menu will remain thin
     * the formula for the body height is
     * body height minus (   site header ; site footer ; guide (if exists)   ) 
     */
    
    var body_height = $$('body')[0].getSize().y;
    var site_header_height = $$('.site-header')[0].getSize().y;
    var site_footer_height = $$('.site-footer')[0].getSize().y;

    var guide_height = 0
    var trial_bar_height = 0
    
    var guide_element = $$('.com-guide.com-005g')[0]
    
    if ( guide_element )
        guide_height = guide_element.getSize().y
    
    if ( $('page').getSize().y  < body_height  ){
        $('main').setStyle( "min-height", ( body_height - ( site_header_height+site_footer_height+guide_height  ) ))
    }
}



function generic_close_dialog(){
    $$('div.ui-dialog').hide()
    $$("#overlay").hide();
}


function generic_open_dialog( ui_container ){
    console.log('generic open dialog')
    ui_container.show()
    $$("#overlay").show();
}



window.addEvent('domready', function(){ 

	var c = new Controller();
    
    /* UI team code */
    
    // setup menu for mobile devides
    nav = $$('#site-navigation')
    if ( nav ){
    	button = $$('#site-navigation .menu-toggle')
        if ( button ){
        $$('#site-navigation .menu-toggle').addEvent('click', function(e){
        		e.preventDefault();
        		nav.toggleClass('toggled-on')
        	})    	
        }
        
        // sets the click event for the nav menu
        $$('#site-navigation .nav-menu-pri .nav-menu-logs > a').addEvent('click', function(e){
        	e.preventDefault()
        	// $$('#site-navigation .nav-menu-pri .nav-menu-logs').toggleClass('selected');
            $$('#site-navigation').addClass('menu-active');
			$$('.nav-menu-logs').addClass('selected');
			$$('.nav-menu-sett').removeClass('selected');
        })	

        // sets the click event for settings menu
        $$('#site-navigation .nav-menu-sec .nav-menu-sett > a').addEvent('click', function(e){
            e.preventDefault()
        	// $$('#site-navigation .nav-menu-sec .nav-menu-sett').toggleClass('selected')
            $$('#site-navigation').addClass('menu-active');
			$$('.nav-menu-sett').addClass('selected');
			$$('.nav-menu-logs').removeClass('selected');
    
        });
        $$('.nav-menu-logs > a, .nav-menu-sett > a').addEvent('click', function(e){
			e.stopPropagation();
		});

        $$(".ui-dialog .dismiss-link, .ui-dialog .cncl-lnk, .ui-dialog .skip-lnk").removeEvents();
        $$(".ui-dialog .dismiss-link, .ui-dialog .cncl-lnk, .ui-dialog .skip-lnk").addEvent( 'click', function( e ){
            e.preventDefault();
            generic_close_dialog();
        } )
        
    }
    
    // do the dynamic page thingy
    setFooter();
    
    
    
    
});
