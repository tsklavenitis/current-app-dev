import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# Create the message
msg = MIMEMultipart()
msg['Subject'] = "Test Email"
msg['From'] = "riskmanagement@avax.gr"
msg['To'] = "ahadjipanayis@avax.gr"
msg.attach(MIMEText("This is a test email", 'plain'))

# SMTP server configuration
smtp_host = 'smtp.avax.gr'
smtp_port = 587
smtp_user = 'riskmanagement@avax.gr'
smtp_password = 'Fi39#d9%'  # Replace with your actual password

# Encode username and password in Base64
encoded_user = base64.b64encode(smtp_user.encode()).decode()
encoded_password = base64.b64encode(smtp_password.encode()).decode()

try:
    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.set_debuglevel(1)  # Enable debug output
    server.ehlo()
    server.starttls()  # Secure the connection
    server.ehlo()

    # Perform AUTH LOGIN manually
    server.docmd("AUTH LOGIN", encoded_user)
    server.docmd(encoded_password)

    # Send the email
    server.sendmail(msg['From'], [msg['To']], msg.as_string())
    server.quit()
    print("Email sent successfully")
except smtplib.SMTPResponseException as e:
    print(f"Failed to send email. SMTP error code: {e.smtp_code}, Message: {e.smtp_error}")
except Exception as e:
    print(f"Failed to send email: {e}")
