import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

def send_invite_email(from_user, recipient_email, invite_link, organization_name):
    # Mailtrap credentials
    smtp_server = settings.MAILTRAP_HOST
    port = settings.MAILTRAP_PORT
    login = settings.MAILTRAP_USERNAME
    password = settings.MAILTRAP_PASSWORD
    
    recipient_email = "ugalock@gmail.com" # TODO: change to recipient_email after testing
    # Email content
    msg = MIMEMultipart()
    msg['Subject'] = f"Invitation to join {organization_name}"
    msg['From'] = "noreply@demomailtrap.co"
    msg['To'] = recipient_email
    
    html = f"""
    <html>
      <body>
        <h2>You've been invited to join {organization_name} by {from_user}!</h2>
        <p>Click <a href="{invite_link}">here</a> to accept the invitation.</p>
        <p>Invitation link expires in 7 days.</p>
        <p>If you don't want to join, you can ignore this email.</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    # Send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        
    return "Email sent to Mailtrap inbox"
