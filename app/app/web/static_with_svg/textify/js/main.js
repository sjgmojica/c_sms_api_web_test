window.onload = function() {
    
    $$(".terms-link").addEvent("click", function(event) {
        event.preventDefault();
        $$("body").set("data-state-dialog", "active");
        $$(".com-terms").set("data-view", "active");
    });
    
    $$(".com-terms .action-link-close").addEvent("click", function(event) {
        event.preventDefault();
        $$("body").set("data-state-dialog", "inactive");
        $$(".com-terms").set("data-view", "inactive");
    });
}

