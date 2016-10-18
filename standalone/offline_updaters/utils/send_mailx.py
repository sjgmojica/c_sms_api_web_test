import smtplib 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Charset

html = """

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<!-- If you delete this meta tag, Half Life 3 will never be released. -->
<meta name="viewport" content="width=device-width" />

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Chikka API</title>
	
</head>
 
<body bgcolor="#FFFFFF" style="width:100%; height:100%; margin:0; font-family:Arial; font-size:16px;">

<!-- BODY -->
<table class="body-wrap" cellpadding="0" cellspacing="0" style="width:100%; box-sizing:border-box; table-layout:fixed; max-width:37.5em; margin:auto;">
	<tr>

		<td class="container" bgcolor="#FFFFFF"style="display:block;margin:0 auto; clear:both; border:1px solid #435D74;">
            <div class="header-content" style="margin:0 auto; display:block; background-color: #435D74; padding:1em 1.5em;">
                <img src="http://api.chikka.com/static/img/webmail-02.png" width="123px" height="33px">
            </div>
			<div class="content" style="padding:2em;margin: 0px auto; display: block; width:100%; box-sizing: border-box; word-wrap: break-word;">
                {0}
                <div class="closing" style="margin-top:2em;">
                    <p style="margin:0;">Thanks!</p>
                    <p style="margin:0;">Chikka API Team</p>
                </div>
			</div><!-- /content -->
									
		</td>

	</tr>
</table><!-- /BODY -->

<!-- FOOTER -->
<table class="footer-wrap" style="margin:0 auto;">
	<tr>
		<td></td>
		<td class="container">
            <!-- content -->
            <div class="content" style="text-align:center;">                
                <p>

                    <a href="https://api.chikka.com/terms-conditions">Terms</a> |
                    <a href="https://api.chikka.com/privacy">Privacy</a>
                </p>
			</div><!-- /content -->	
		</td>
		<td></td>
	</tr>
</table><!-- /FOOTER -->

</body>
</html>
"""

def send_mailx(text_content, html_content, subject, to_, email_from_, mail_host, mail_port):
    '''
    generic smtp function. sends email based on arguments
    ''' 
        
    try:
        
        text_content = html.format(str(text_content))
        html_content = html.format(str(html_content))
                
        if isinstance(to_, list):
            to_ = ', '.join(to_)

        # Override python's weird assumption that utf-8 text should be encoded with
        # base64, and instead use quoted-printable (for both subject and body).  I
        # can't figure out a way to specify QP (quoted-printable) instead of base64 in
        # a way that doesn't modify global state. :-(
        Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
        
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        
        msg['Subject'] = subject
        msg['From'] = email_from_
            
        msg['To'] = to_
        
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text_content.encode('utf-8'), 'plain', 'UTF-8')
        part2 = MIMEText(html_content.encode('utf-8'), 'html', 'UTF-8')
        
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)


        mail_host = mail_host 
        mail_port = mail_port 
        
        server = smtplib.SMTP(host=mail_host, port=mail_port)
        
        server.sendmail('no-reply@chikkasmsapiadmin', to_, msg.as_string())
        server.quit()

         

    except Exception, e:
        # print e
        import traceback
        print traceback.format_exc()