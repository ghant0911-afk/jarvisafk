"""
Calendar integration for Jarvis.
Supports local calendar storage and reminders.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict


@dataclass
class CalendarEvent:
    id: str
    title: str
    description: str
    start_time: str  # ISO format
    end_time: str  # ISO format
    reminder_minutes: int = 15
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class Calendar:
    """Simple local calendar storage."""

    def __init__(self, storage_path: str = "data/calendar.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: List[CalendarEvent] = []
        self._load()

    def _load(self):
        """Load events from storage."""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.events = [CalendarEvent(**event) for event in data]
            except Exception:
                self.events = []

    def _save(self):
        """Save events to storage."""
        try:
            data = [asdict(event) for event in self.events]
            self.storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def add_event(self, title: str, start_time: datetime, duration_minutes: int = 60,
                  description: str = "", reminder_minutes: int = 15) -> CalendarEvent:
        """Add new event to calendar."""
        event_id = datetime.now().strftime("%Y%m%d%H%M%S")
        end_time = start_time + timedelta(minutes=duration_minutes)

        event = CalendarEvent(
            id=event_id,
            title=title,
            description=description,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            reminder_minutes=reminder_minutes,
        )

        self.events.append(event)
        self._save()
        return event

    def get_events_today(self) -> List[CalendarEvent]:
        """Get all events for today."""
        today = datetime.now().date()
        result = []

        for event in self.events:
            event_date = datetime.fromisoformat(event.start_time).date()
            if event_date == today:
                result.append(event)

        return sorted(result, key=lambda e: e.start_time)

    def get_upcoming_events(self, days: int = 7) -> List[CalendarEvent]:
        """Get upcoming events for next N days."""
        now = datetime.now()
        future = now + timedelta(days=days)
        result = []

        for event in self.events:
            event_time = datetime.fromisoformat(event.start_time)
            if now <= event_time <= future:
                result.append(event)

        return sorted(result, key=lambda e: e.start_time)

    def delete_event(self, event_id: str) -> bool:
        """Delete event by ID."""
        for i, event in enumerate(self.events):
            if event.id == event_id:
                self.events.pop(i)
                self._save()
                return True
        return False

    def search_events(self, query: str) -> List[CalendarEvent]:
        """Search events by title or description."""
        query_lower = query.lower()
        result = []

        for event in self.events:
            if (query_lower in event.title.lower() or
                query_lower in event.description.lower()):
                result.append(event)

        return sorted(result, key=lambda e: e.start_time)


def parse_datetime_from_text(text: str) -> Optional[datetime]:
    """
    Parse datetime from natural language text.
    Examples:
    - "завтра в 15:00"
    - "через 2 часа"
    - "в пятницу в 10:00"
    """
    now = datetime.now()
    text_lower = text.lower().strip()

    # "через X часов/минут"
    if "через" in text_lower:
        import re
        # Try to find number
        match = re.search(r'(\d+)', text_lower)
        if match:
            number = int(match.group(1))
            if "час" in text_lower:
                return now + timedelta(hours=number)
            elif "минут" in text_lower:
                return now + timedelta(minutes=number)
        # If no number found, assume 1
        elif "час" in text_lower:
            return now + timedelta(hours=1)
        elif "минут" in text_lower:
            return now + timedelta(minutes=1)

    # "завтра"
    if "завтра" in text_lower:
        tomorrow = now + timedelta(days=1)
        # Try to extract time
        if "в" in text_lower and ":" in text_lower:
            try:
                import re
                time_match = re.search(r'(\d{1,2}):(\d{2})', text_lower)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except (ValueError, IndexError):
                pass
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

    # "сегодня"
    if "сегодня" in text_lower:
        if "в" in text_lower and ":" in text_lower:
            try:
                import re
                time_match = re.search(r'(\d{1,2}):(\d{2})', text_lower)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except (ValueError, IndexError):
                pass

    return None


def format_event(event: CalendarEvent) -> str:
    """Format event for display."""
    start = datetime.fromisoformat(event.start_time)
    end = datetime.fromisoformat(event.end_time)

    return (
        f"📅 {event.title}\n"
        f"🕐 {start.strftime('%d.%m.%Y %H:%M')} - {end.strftime('%H:%M')}\n"
        f"📝 {event.description if event.description else 'Без описания'}\n"
        f"⏰ Напоминание за {event.reminder_minutes} мин"
    )


def format_events_list(events: List[CalendarEvent]) -> str:
    """Format list of events."""
    if not events:
        return "Нет событий."

    output = []
    for event in events:
        start = datetime.fromisoformat(event.start_time)
        output.append(f"• {start.strftime('%d.%m %H:%M')} - {event.title}")

    return "\n".join(output)
