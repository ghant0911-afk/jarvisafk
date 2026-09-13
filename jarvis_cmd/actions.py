"""
Actions system for Jarvis - like JARVIS from Iron Man.
Handles complex multi-step tasks and integrations.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from jarvis_cmd.web_search import search_web, search_wikipedia, get_weather, format_search_results, format_weather
from jarvis_cmd.calendar_manager import Calendar, parse_datetime_from_text, format_event, format_events_list
from jarvis_cmd.logger import get_logger

logger = get_logger()


@dataclass
class ActionResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class JarvisActions:
    """High-level actions that Jarvis can perform."""

    def __init__(self):
        self.calendar = Calendar()

    def search_internet(self, query: str) -> ActionResult:
        """Search the internet for information."""
        logger.info(f"Searching internet: {query}")

        # Try Wikipedia first for factual queries
        if any(word in query.lower() for word in ["что такое", "кто такой", "что это", "определение"]):
            wiki_result = search_wikipedia(query)
            if wiki_result:
                return ActionResult(
                    success=True,
                    message=f"📚 Wikipedia:\n\n{wiki_result}",
                    data={"source": "wikipedia", "query": query}
                )

        # General web search
        results = search_web(query)
        if results:
            formatted = format_search_results(results)
            return ActionResult(
                success=True,
                message=f"🔍 Результаты поиска:\n\n{formatted}",
                data={"source": "web", "query": query, "count": len(results)}
            )

        return ActionResult(
            success=False,
            message="Не удалось найти информацию в интернете."
        )

    def get_weather_info(self, city: str = "Moscow") -> ActionResult:
        """Get current weather."""
        logger.info(f"Getting weather for: {city}")

        weather = get_weather(city)
        if weather:
            formatted = format_weather(weather)
            return ActionResult(
                success=True,
                message=f"🌤️ Погода в {city}:\n\n{formatted}",
                data=weather
            )

        return ActionResult(
            success=False,
            message=f"Не удалось получить погоду для {city}."
        )

    def add_calendar_event(self, title: str, when: str, description: str = "") -> ActionResult:
        """Add event to calendar."""
        logger.info(f"Adding calendar event: {title} at {when}")

        # Parse datetime from natural language
        event_time = parse_datetime_from_text(when)
        if not event_time:
            return ActionResult(
                success=False,
                message=f"Не удалось понять время: '{when}'. Попробуй 'завтра в 15:00' или 'через 2 часа'."
            )

        # Add event
        event = self.calendar.add_event(
            title=title,
            start_time=event_time,
            description=description,
            duration_minutes=60
        )

        formatted = format_event(event)
        return ActionResult(
            success=True,
            message=f"✅ Событие добавлено:\n\n{formatted}",
            data={"event_id": event.id}
        )

    def show_calendar(self, period: str = "today") -> ActionResult:
        """Show calendar events."""
        logger.info(f"Showing calendar: {period}")

        if period == "today":
            events = self.calendar.get_events_today()
            title = "📅 События на сегодня"
        else:
            events = self.calendar.get_upcoming_events(days=7)
            title = "📅 События на неделю"

        if not events:
            return ActionResult(
                success=True,
                message=f"{title}:\n\nНет событий."
            )

        formatted = format_events_list(events)
        return ActionResult(
            success=True,
            message=f"{title}:\n\n{formatted}",
            data={"count": len(events)}
        )

    def get_time_info(self) -> ActionResult:
        """Get current time and date."""
        now = datetime.now()

        weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        weekday = weekdays[now.weekday()]

        message = (
            f"🕐 Текущее время: {now.strftime('%H:%M:%S')}\n"
            f"📅 Дата: {now.strftime('%d.%m.%Y')}\n"
            f"📆 День недели: {weekday}"
        )

        return ActionResult(
            success=True,
            message=message,
            data={"timestamp": now.isoformat()}
        )

    def set_reminder(self, text: str, when: str) -> ActionResult:
        """Set a reminder."""
        return self.add_calendar_event(
            title=f"⏰ Напоминание: {text}",
            when=when,
            description=text
        )


# Global instance
_actions: Optional[JarvisActions] = None


def get_actions() -> JarvisActions:
    """Get or create global actions instance."""
    global _actions
    if _actions is None:
        _actions = JarvisActions()
    return _actions
