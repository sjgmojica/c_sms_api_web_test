var ControllerShortcode = function() {
    this.onClick = function() {
        
        if ($("tutorial-shortcode")) {
            $("tutorial-shortcode")
            $("tutorial-shortcode").addEvent("click", function(e) {
                e.preventDefault();
                $$(".com-tutorial-short-code")[0].show();
                $$("#overlay").show();
            });
                
            /* shortcode */
            

        }
            
        /* pop up use shortcode confirmation*/
        
        if($$(".use-shortcode")) {
            $$(".use-shortcode").removeEvents();
            $$(".use-shortcode").addEvent("click", function(e){
                e.preventDefault();
                $(this).getParent().getElement("div[class*=ui-dialog]").setStyle("display", "block");
                $("overlay").setStyle("display", "block");
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
    new ControllerShortcode();
});

