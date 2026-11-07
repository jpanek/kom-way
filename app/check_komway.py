
import os
import requests
import smtplib

from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_URL = "https://kom-way.cyclingdatahub.com/api/v1/full-weather"
STATE_FILE = BASE_DIR / "api_status.txt"

DOCS_URL = "https://kom-way.cyclingdatahub.com/docs#"
STATUS_URL = "https://kom-way.cyclingdatahub.com/status?key=juraj"

TIMEOUT = 20

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")


# --------------------------------------------------
# Email notification
# --------------------------------------------------

def send_email(subject, body):
    required = {
        "SMTP_USER": SMTP_USER,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "EMAIL_FROM": EMAIL_FROM,
        "EMAIL_TO": EMAIL_TO,
    }

    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing .env settings: " + ", ".join(missing)
        )

    # Supports single or multiple comma-separated addresses
    recipients = [
        address.strip()
        for address in EMAIL_TO.split(",")
        if address.strip()
    ]

    if not recipients:
        raise RuntimeError("EMAIL_TO contains no recipients.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg, to_addrs=recipients)


# --------------------------------------------------
# API health check
# --------------------------------------------------

def check_api():
    payload = {
        "latitude": 0,
        "longitude": 0,
        "device_id": "-1",
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            return True, "HTTP 200 OK"

        return False, (
            f"HTTP {response.status_code}: {response.text[:300]}"
        )

    except requests.RequestException as exc:
        return False, str(exc)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    timestamp = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    # Assume UP on first run
    previous_state = (
        STATE_FILE.read_text(encoding="utf-8").strip()
        if STATE_FILE.exists()
        else "UP"
    )

    is_up, details = check_api()
    is_up = False
    current_state = "UP" if is_up else "DOWN"

    print(
        f"[{timestamp}] Kom-Way API: "
        f"{current_state} - {details}"
    )

    # No state change - no notification
    if current_state == previous_state:
        return

    links = (
        "\n\nUseful links:\n"
        f"API Documentation: {DOCS_URL}\n"
        f"Monitoring Dashboard: {STATUS_URL}\n"
    )

    if current_state == "DOWN":
        subject = "[ALERT] Kom-Way API is DOWN"

        body = (
            "Kom-Way API is not responding.\n\n"
            f"Time: {timestamp}\n"
            f"Details: {details}"
            f"{links}"
        )

    else:
        subject = "[RECOVERY] Kom-Way API is back ONLINE"

        body = (
            "Kom-Way API is responding again.\n\n"
            f"Time: {timestamp}\n"
            f"Status: {details}"
            f"{links}"
        )

    # Update state only after successful email delivery
    try:
        send_email(subject, body)

        print(f"[{timestamp}] Notification email sent.")

        STATE_FILE.write_text(
            current_state,
            encoding="utf-8",
        )

    except Exception as exc:
        print(
            f"[{timestamp}] Failed to send notification: {exc}"
        )


if __name__ == "__main__":
    main()
