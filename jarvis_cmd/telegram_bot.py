from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Load .env file if exists
try:
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
except Exception:
    pass

from jarvis_cmd.brain import plan_command
from jarvis_cmd.executor import run_command
from jarvis_cmd.memory import append_history
from jarvis_cmd.safety import check_command
from jarvis_cmd.speech import SpeechError, transcribe_audio
from jarvis_cmd.telegram_http import download_file, telegram_api
from jarvis_cmd.logger import get_logger
from jarvis_cmd.actions import get_actions
from jarvis_cmd.conversation import get_conversation

logger = get_logger()


def _api(token: str, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return telegram_api(token, method, params)


def _send(token: str, chat_id: str, text: str) -> None:
    try:
        _api(
            token,
            "sendMessage",
            {"chat_id": chat_id, "text": text[:3500]},
        )
    except Exception as exc:
        logger.error(f"Failed to send message: {exc}", exc_info=True)


def _download_telegram_file(token: str, file_id: str, target_path: str) -> None:
    get_file = _api(token, "getFile", {"file_id": file_id})
    file_path = get_file.get("result", {}).get("file_path", "")
    if not file_path:
        raise RuntimeError("Telegram не вернул file_path для голосового сообщения.")
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    payload = download_file(file_url)
    Path(target_path).write_bytes(payload)


def _handle_command(user_text: str) -> Optional[str]:
    """Handle bot commands like /start, /help, /status."""
    text = user_text.strip().lower()

    if text == "/start":
        return (
            "👋 Привет! Я Jarvis - твой голосовой ассистент.\n\n"
            "Отправь мне текстовое или голосовое сообщение с задачей, "
            "и я преобразую его в команду.\n\n"
            "Команды:\n"
            "/help - справка\n"
            "/status - статус системы"
        )

    if text == "/help":
        return (
            "📖 Справка по Jarvis\n\n"
            "Примеры запросов:\n"
            "• Покажи файлы\n"
            "• Текущая папка\n"
            "• Дата и время\n"
            "• Запусти notepad\n\n"
            "Я понимаю текст и голосовые сообщения.\n"
            "Опасные команды блокируются автоматически."
        )

    if text == "/status":
        from jarvis_cmd.brain import _ollama_plan
        ollama_status = "✅ работает" if _ollama_plan("test") else "❌ недоступен"
        return (
            f"🤖 Статус Jarvis\n\n"
            f"Ollama LLM: {ollama_status}\n"
            f"Режим выполнения: {'включен' if os.getenv('TELEGRAM_ALLOW_EXECUTE', 'true').lower() == 'true' else 'отключен'}\n"
            f"Логирование: активно"
        )

    return None


def _handle_text(user_text: str, allow_execute: bool, chat_id: str = "telegram") -> str:
    # Check for bot commands first
    cmd_response = _handle_command(user_text)
    if cmd_response:
        logger.info(f"Bot command: {user_text}")
        return cmd_response

    # Get conversation history for context
    conversation = get_conversation(chat_id)
    history = conversation.get_messages()

    try:
        plan = plan_command(user_text, conversation_history=history)
        logger.debug(f"Plan: intent={plan.intent}, command={plan.command}, source={plan.source}")
    except Exception as exc:
        logger.error(f"Planning error: {exc}", exc_info=True)
        return f"❌ Ошибка планирования: {exc}"

    # Handle chat intent
    if plan.intent == "chat":
        # Save to conversation history
        conversation.add_message("user", user_text)
        conversation.add_message("assistant", plan.reason)

        append_history(
            {
                "source": "telegram",
                "intent": "chat",
                "user": user_text,
                "message": plan.reason,
                "plan_source": plan.source,
            }
        )
        return plan.reason

    # Handle special intents (search, calendar, weather, etc)
    if plan.intent in {"search", "calendar", "weather", "reminder", "time"}:
        try:
            actions = get_actions()
            params = plan.params or {}

            if plan.intent == "search":
                result = actions.search_internet(params.get("query", user_text))
            elif plan.intent == "calendar":
                result = actions.add_calendar_event(
                    title=params.get("title", "Событие"),
                    when=params.get("when", "сегодня"),
                    description=params.get("description", "")
                )
            elif plan.intent == "weather":
                result = actions.get_weather_info(params.get("city", "Moscow"))
            elif plan.intent == "reminder":
                result = actions.set_reminder(
                    text=params.get("text", "Напоминание"),
                    when=params.get("when", "через час")
                )
            elif plan.intent == "time":
                result = actions.get_time_info()

            append_history({
                "source": "telegram",
                "intent": plan.intent,
                "user": user_text,
                "success": result.success,
                "message": result.message[:500],
                "plan_source": plan.source,
            })

            return result.message

        except Exception as exc:
            logger.error(f"Action error: {exc}", exc_info=True)
            return f"❌ Ошибка выполнения: {exc}"

    if plan.intent == "answer" or not plan.command:
        append_history(
            {
                "source": "telegram",
                "intent": "answer",
                "user": user_text,
                "message": plan.reason,
                "plan_source": plan.source,
            }
        )
        return plan.reason

    decision = check_command(plan.command)
    if not decision.allowed:
        append_history(
            {
                "source": "telegram",
                "intent": "execute",
                "user": user_text,
                "command": plan.command,
                "blocked": True,
                "reason": decision.reason,
            }
        )
        return f"⛔ {decision.reason}\nКоманда: {plan.command}"

    if decision.requires_confirmation:
        return (
            "⚠️ Команда рискованная и требует ручного подтверждения.\n"
            "Отправь ее в локальный CLI Jarvis.\n"
            f"Команда: {plan.command}"
        )

    if not allow_execute:
        logger.info(f"Plan only mode: {plan.command}")
        return f"🧠 План: {plan.command}\n(выполнение в Telegram отключено)"

    try:
        result = run_command(plan.command)
        logger.info(f"Command executed: {plan.command}, exit_code={result.exit_code}")
    except Exception as exc:
        logger.error(f"Execution error: {exc}", exc_info=True)
        return f"❌ Ошибка выполнения: {exc}"
    append_history(
        {
            "source": "telegram",
            "intent": "execute",
            "user": user_text,
            "command": plan.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout[:1500],
            "stderr": result.stderr[:1500],
            "plan_source": plan.source,
        }
    )
    parts = [f"✅ Команда: {plan.command}", f"Exit code: {result.exit_code}"]
    if result.stdout:
        parts.append(f"STDOUT:\n{result.stdout[:1000]}")
    if result.stderr:
        parts.append(f"STDERR:\n{result.stderr[:600]}")
    return "\n\n".join(parts)


def _extract_text_from_message(token: str, message: Dict[str, Any]) -> str:
    if "text" in message and message["text"]:
        return str(message["text"])

    voice = message.get("voice")
    if voice and isinstance(voice, dict):
        file_id = str(voice.get("file_id", ""))
        if not file_id:
            raise SpeechError("В voice-сообщении отсутствует file_id.")
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_path = str(Path(temp_dir) / "voice.ogg")
            _download_telegram_file(token, file_id, voice_path)
            return transcribe_audio(voice_path)

    raise SpeechError("Поддерживаются только текст и voice-сообщения.")


def run_bot() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    allow_execute = os.getenv("TELEGRAM_ALLOW_EXECUTE", "true").strip().lower() == "true"
    poll_interval = float(os.getenv("TELEGRAM_POLL_INTERVAL_SEC", "1.5"))

    if not token or not chat_id:
        raise RuntimeError("Нужны TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в окружении.")

    logger.info("Jarvis Telegram Bot starting...")
    print("Jarvis Telegram Bot started.")
    _send(token, chat_id, "[Jarvis] Telegram-бот активирован.")

    offset = 0
    error_count = 0
    max_errors = 10

    while True:
        try:
            response = _api(token, "getUpdates", {"timeout": 20, "offset": offset})
            error_count = 0  # Reset error counter on success

            for item in response.get("result", []):
                offset = int(item["update_id"]) + 1
                message = item.get("message", {})
                msg_chat_id = str((message.get("chat") or {}).get("id", ""))

                if msg_chat_id != chat_id:
                    logger.debug(f"Ignoring message from chat_id={msg_chat_id}")
                    continue

                try:
                    user_text = _extract_text_from_message(token, message)
                    logger.info(f"Received message: {user_text[:100]}")
                    answer = _handle_text(user_text, allow_execute=allow_execute, chat_id=chat_id)
                except SpeechError as exc:
                    answer = f"🎤 Ошибка распознавания: {exc}"
                    logger.warning(f"Speech error: {exc}")
                except Exception as exc:
                    answer = f"❌ Ошибка: {exc}"
                    logger.error(f"Message handling error: {exc}", exc_info=True)

                _send(token, chat_id, answer)

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("\nBot stopped.")
            break
        except Exception as exc:
            error_count += 1
            logger.error(f"Bot loop error ({error_count}/{max_errors}): {exc}", exc_info=True)

            if error_count >= max_errors:
                logger.critical(f"Too many errors ({max_errors}), stopping bot")
                _send(token, chat_id, "[Jarvis] ⚠️ Бот остановлен из-за множественных ошибок")
                raise

            # Exponential backoff
            sleep_time = min(poll_interval * (2 ** error_count), 60)
            logger.info(f"Retrying in {sleep_time}s...")
            time.sleep(sleep_time)


if __name__ == "__main__":
    run_bot()
