import os
from typing import Optional

from jarvis_cmd.telegram_http import telegram_api


class TelegramNotifier:
    def __init__(self) -> None:
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            data = telegram_api(
                self.token,
                "sendMessage",
                {
                    "chat_id": self.chat_id,
                    "text": text[:3500],
                },
            )
            return bool(data.get("ok"))
        except Exception:
            return False


def format_event(title: str, body: Optional[str] = None) -> str:
    if body:
        return f"[Jarvis] {title}\n{body}"
    return f"[Jarvis] {title}"
