import hashlib
import os
import smtplib
from email.message import EmailMessage
import requests

PDF_URL = os.environ.get("SCHEDULE_PDF_URL")
SENDER_EMAIL = os.environ.get("MAIL_USER")
SENDER_PASSWORD = os.environ.get("MAIL_PASS")
RECEIVER_EMAIL = "maciejpikula@int.pl"

HASH_FILE = "last_hash.txt"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587


def get_pdf_hash(url):
  if not url:
    raise ValueError("Brak adresu URL pliku PDF w zmiennej SCHEDULE_PDF_URL.")
  response = requests.get(url)
  response.raise_for_status()
  return hashlib.sha256(response.content).hexdigest()


def send_email_alert():
  msg = EmailMessage()
  msg["Subject"] = "Zaktualizowano plan zajęć na uczelni"
  msg["From"] = SENDER_EMAIL
  msg["To"] = RECEIVER_EMAIL
  msg.set_content(
      "Plik PDF na stronie uczelni zmienił się. Sprawdź najnowszą wersję"
      f" planu:\n{PDF_URL}"
  )

  with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
  print("Wysłano powiadomienie e-mail o zmianie planu.")


def main():
  current_hash = get_pdf_hash(PDF_URL)

  previous_hash = ""
  if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r") as f:
      previous_hash = f.read().strip()

  if current_hash != previous_hash:
    print("Wykryto zmianę w pliku PDF.")
    send_email_alert()

    with open(HASH_FILE, "w") as f:
      f.write(current_hash)
  else:
    print("Brak zmian w pliku PDF.")


if __name__ == "__main__":
  main()
