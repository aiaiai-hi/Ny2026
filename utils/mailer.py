import smtplib
from email.mime.text import MIMEText

def send_email(day):
    sender_email = "no-reply@adventapp.com"
    recipient_email = "anna_ts@inbox.ru"
    subject = f"Tanya completed her Day {day} task!"
    body = f"Tanya has completed her task for Day {day}. You can check the app for uploaded content."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            # !!! Здесь можно ввести свой логин/пароль от почты !!!
            # server.login("YOUR_EMAIL", "YOUR_PASSWORD")
            # server.send_message(msg)
            print(f"[DEBUG] Email sent to {recipient_email}")
    except Exception as e:
        print(f"Email error: {e}")
