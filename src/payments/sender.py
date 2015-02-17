from payments.config import email_user, email_pass

import smtplib
from email.mime.text import MIMEText


def send_mail(to, subject, body):
    # Create a text/plain message
    msg = MIMEText(body)
    
    msg['From'] = email_user
    msg['To'] = to
    msg['Subject'] = subject
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_user, email_pass)
    server.sendmail(email_user, [to], msg.as_string())
    server.close()
