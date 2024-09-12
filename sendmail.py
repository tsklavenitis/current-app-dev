import smtplib

smtp_host = 'smtp.avax.gr'
smtp_port = 587
smtp_user = 'riskmanagement@avax.gr'
smtp_password = 'Fi39#d9%'  # Replace with your actual password

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_user, smtp_password)
    server.sendmail(
        'riskmanagement@avax.gr',
        'ahadjipanayis@avax.gr',
        'Subject: Test Email\n\nThis is a test email.'
    )
