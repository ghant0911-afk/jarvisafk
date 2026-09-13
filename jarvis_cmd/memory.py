import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from jarvis_cmd.config import get_config

def _get_history_path() -> Path:
    config = get_config()
    return Path(config.get_history_path())

HISTORY_PATH = _get_history_path()
FACTS_PATH = HISTORY_PATH.parent / "facts.json"

def append_history(entry: Dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **entry,
    }
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

def save_fact(fact: str) -> str:
    """Сохраняет факт в долговременную память (Hermes Agent Concept)"""
    FACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    facts = get_all_facts()
    if fact not in facts:
        facts.append(fact)
        FACTS_PATH.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"Факт сохранен: {fact}"
    return f"Я уже знаю этот факт: {fact}"

def get_all_facts() -> List[str]:
    """Возвращает все сохраненные факты для промпта"""
    if not FACTS_PATH.exists():
        return []
    try:
        return json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    except:
        return []

def delete_fact(fact: str) -> str:
    facts = get_all_facts()
    if fact in facts:
        facts.remove(fact)
        FACTS_PATH.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"Факт удален: {fact}"
    return "Такого факта нет в памяти."