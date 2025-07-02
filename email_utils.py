import smtplib
from email.message import EmailMessage

def send_email(sender_email, app_password, recipient, subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending to {recipient}: {e}")
        return False
