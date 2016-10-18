/*
    @author: Jhesed Tacadena
    @date: 2013-10
    @description:
        - handles polling in determining
        whether an MT message was successfully sent
*/

window.addEvent('domready', function(){
    if ($('testmin_chars') != null) {
        var testmin = document.id('testmin_chars').get('value');
        poll_url = '/message/sent?mobile=' + testmin;
       
        if (document.id('message_id')) {
            var message_id = document.id('message_id').get('value'); 
            poll_url += '&message_id=' + message_id;
        }
        
        isMessageSent = function() {
            if (testmin && testmin != 'None') {
                var verification_request = new Request({
                    method: 'get',
                    url: poll_url,
                    initialDelay: 1000,
                    delay: 3000,
                    limit: 8000,
                    onSuccess: function(response_text){
                        if(response_text == 'SUCCESS'){
                            $('mt_notification_success_message').set('text', 'You have successfully sent your Test SMS.');
                            $('mt_notification_success').setStyle('display', 'block');      
                            verification_request.stopTimer();
                        }    
                        else if(response_text == 'FAIL'){
                            $('mt_notification_fail_message').set('text', 'Oops! Something went wrong while sending your message. Please try again later.');
                            $('mt_notification_fail').setStyle('display', 'block');
                            verification_request.stopTimer();
                        }
                    }
                });
                verification_request.startTimer();
                } 
        }
        
        if (document.id('message_id') && testmin && testmin != 'None') {
            $('mt_notification_success').setStyle('display', 'none'); 
            $('mt_notification_fail').setStyle('display', 'none');        
            isMessageSent();
        }
    }
});