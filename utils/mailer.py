import smtplib
from email.mime.text import MIMEText

def send_email(day: int) -> bool:
    sender_email = "platya4@gmail.com"      # твоя 
    sender_password = "Wsreyjdf85!"      # пароль приложения
    recipient_email = "anna_ts@inbox.ru"

    subject = f"Tanya completed her Day {day} task!"
    body = f"Tanya has completed the task for Day {day}. Check her Advent Calendar app."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # Автоматически определяем SMTP сервер по домену почты
    if "mail.ru" in sender_email:
        smtp_server, smtp_port = "smtp.mail.ru", 587
    elif "yandex" in sender_email:
        smtp_server, smtp_port = "smtp.yandex.ru", 465
    else:
        smtp_server, smtp_port = "smtp.gmail.com", 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {recipient_email}.")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False
