import smtplib
from email.mime.text import MIMEText

def send_email(body, subject, recipients, host_user=None, host_pass=None, 
                body_type='plain'):
    
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(
        host_user if host_user else "microworkers.gmail.com", 
        host_pass if host_pass else 123456
    )
    
    sender = 'microworkers@microworkers.com'
    msg = MIMEText(body, body_type)
    msg['subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    session.sendmail(sender, recipients, msg.as_string())