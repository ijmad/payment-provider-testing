import os, smtplib
from email.mime.text import MIMEText

def send_mail(to, subject, body):
    # Create a text/plain message
    msg = MIMEText(body)
    
    msg['From'] = os.environ['MAIL_FROM']
    msg['To'] = to
    msg['Subject'] = subject
    
    server = smtplib.SMTP(os.environ['MAIL_SERVER'], os.environ['MAIL_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(os.environ['MAIL_USER'], os.environ['MAIL_PASS'])
    server.sendmail(os.environ['MAIL_USER'], [to], msg.as_string())
    server.close()
