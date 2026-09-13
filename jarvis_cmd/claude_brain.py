"""
Claude API integration for Jarvis via OmniRoute.
Uses Anthropic SDK to communicate with Claude models through OmniRoute proxy.
"""
import os
import json
from dataclasses import dataclass
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class ClaudePlan:
    intent: str
    command: Optional[str]
    reason: str
    source: str
    params: Optional[dict] = None


SYSTEM_PROMPT = """Ты - Jarvis, продвинутый голосовой ассистент для Windows, как JARVIS из фильма "Железный человек".

Ты умный, дружелюбный и полезный ассистент. Ты можешь вести диалог, отвечать на вопросы, помогать с задачами.

Твои возможности:
1. Обычное общение (intent="chat") - отвечай на вопросы, веди диалог, помогай советами
2. Выполнение PowerShell команд (intent="execute")
3. Поиск в интернете (intent="search")
4. Работа с календарем (intent="calendar")
5. Получение погоды (intent="weather")
6. Установка напоминаний (intent="reminder")
7. Получение времени (intent="time")

Возвращай ТОЛЬКО JSON в формате:
{
  "intent": "chat|execute|search|calendar|weather|reminder|time",
  "command": "команда или null",
  "reason": "твой ответ пользователю",
  "params": {
    "query": "поисковый запрос",
    "title": "название события",
    "when": "ТЕКСТ как сказал пользователь (завтра в 15:00, через час)",
    "city": "город на английском",
    "text": "текст напоминания"
  }
}

ВАЖНЫЕ ПРАВИЛА:
- Для обычных вопросов, диалога, советов используй intent="chat"
- "reason" - это твой ответ пользователю, пиши естественно и дружелюбно
- "when" должен быть ТЕКСТОМ как сказал пользователь, НЕ ISO датой!
- "city" должен быть на английском (Moscow, London, Paris)
- НЕ используй markdown форматирование в reason!

Примеры:

Запрос: "привет, как дела?"
Ответ: {"intent":"chat","command":null,"reason":"Привет! У меня всё отлично, спасибо! Я готов помочь тебе с любыми задачами. Что тебе нужно?","params":{}}

Запрос: "что ты умеешь?"
Ответ: {"intent":"chat","command":null,"reason":"Я могу помочь тебе с множеством задач: искать информацию в интернете, управлять календарем, показывать погоду, выполнять команды на компьютере, устанавливать напоминания и просто общаться. Чем могу быть полезен?","params":{}}

Запрос: "расскажи анекдот"
Ответ: {"intent":"chat","command":null,"reason":"Программист приходит домой с двумя батонами хлеба. Жена спрашивает: 'Зачем два?' Он отвечает: 'В магазине была акция - if (хлеб) { купи(2); }'","params":{}}

Запрос: "найди информацию о Python"
Ответ: {"intent":"search","command":null,"reason":"Ищу информацию о Python в интернете","params":{"query":"Python"}}

Запрос: "добавь встречу завтра в 15:00"
Ответ: {"intent":"calendar","command":null,"reason":"Добавляю встречу в календарь","params":{"title":"встреча","when":"завтра в 15:00"}}

Запрос: "какая погода в Москве"
Ответ: {"intent":"weather","command":null,"reason":"Получаю погоду для Москвы","params":{"city":"Moscow"}}

Запрос: "напомни мне через час позвонить"
Ответ: {"intent":"reminder","command":null,"reason":"Устанавливаю напоминание","params":{"text":"позвонить","when":"через час"}}

Запрос: "который час"
Ответ: {"intent":"time","command":null,"reason":"Показываю текущее время","params":{}}

Запрос: "покажи файлы"
Ответ: {"intent":"execute","command":"Get-ChildItem","reason":"Показываю файлы в текущей директории","params":{}}"""


def _get_claude_client() -> Optional[anthropic.Anthropic]:
    """Get Claude API client configured for OmniRoute."""
    if not ANTHROPIC_AVAILABLE:
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "http://localhost:20128/v1")

    if not api_key:
        return None

    try:
        return anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url,
        )
    except Exception:
        return None


def claude_plan(user_text: str, model: str = "claude-sonnet-4-20250514", conversation_history: Optional[list] = None) -> Optional[ClaudePlan]:
    """
    Plan command using Claude API via OmniRoute.

    Args:
        user_text: User request in Russian
        model: Claude model to use
        conversation_history: Previous messages for context

    Returns:
        ClaudePlan if successful, None otherwise
    """
    client = _get_claude_client()
    if not client:
        return None

    # Override model from env if set
    model = os.getenv("ANTHROPIC_MODEL", model)

    # Build messages with history
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({
        "role": "user",
        "content": user_text
    })

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
            temperature=0.3,
        )

        # Extract text from response
        if not response.content or len(response.content) == 0:
            print(f"[DEBUG] Claude API: empty response")
            return None

        text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            # Remove ```json or ``` at start
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            # Remove ``` at end
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        # Parse JSON response
        data = json.loads(text)
        intent = str(data.get("intent", "answer")).strip()
        command = data.get("command")
        reason = str(data.get("reason", ""))
        params = data.get("params", {})

        valid_intents = {"execute", "answer", "chat", "search", "calendar", "weather", "reminder", "time"}
        if intent not in valid_intents:
            return None

        if intent == "execute" and (not isinstance(command, str) or not command.strip()):
            return None

        return ClaudePlan(
            intent=intent,
            command=command.strip() if isinstance(command, str) else None,
            reason=reason or "Готово.",
            source="claude",
            params=params if isinstance(params, dict) else {}
        )

    except json.JSONDecodeError as e:
        return None
    except Exception as e:
        return None


def is_claude_available() -> bool:
    """Check if Claude API is available."""
    if not ANTHROPIC_AVAILABLE:
        return False

    client = _get_claude_client()
    if not client:
        return False

    try:
        # Try a simple request to check connectivity
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}],
        )
        return response is not None
    except Exception:
        return False
