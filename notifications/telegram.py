import requests
from django.conf import settings
from requests import Response

TELEGRAM_SEND_MESSAGE_URL = (
    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
)


def send_telegram_notification(message: str) -> Response:
    return requests.post(
        TELEGRAM_SEND_MESSAGE_URL,
        data={
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
        },
    )
