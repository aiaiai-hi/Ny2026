import smtplib
from email.mime.text import MIMEText

def send_email(day: int):
    """
    Sends an email notification to the parent when Tanya completes her task.
    Works with Gmail, Mail.ru or Yandex — just change SMTP settings accordingly.
    """

    # === CONFIGURATION ===
    sender_email = "platya4@gmail.com"          # ⚠️ Укажи свою почту-отправителя
    sender_password = "Wsreyjdf85!"          # ⚠️ Пароль приложения (не обычный!)
    recipient_email = "anna_ts@inbox.ru"           # Куда отправлять уведомления

    # === MESSAGE BODY ===
    subject = f"Tanya completed her Day {day} task!"
    body = f"""
    Hello!

    Tanya has just completed her Advent Calendar task for Day {day}. 
    Check her Advent Quest app to view what she submitted.

    — Santa's Notification Bot 🎅
    """

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # === SMTP SERVER (Gmail by default) ===
    # Если ты используешь Mail.ru или Yandex, поменяй настройки ниже:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Для Mail.ru:
    # smtp_server = "smtp.mail.ru"
    # smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {recipient_email} for Day {day}.")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
