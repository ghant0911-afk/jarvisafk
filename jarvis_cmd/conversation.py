"""
Conversation history manager for Jarvis.
Stores recent messages to provide context for chat.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ConversationHistory:
    """Manages conversation history for contextual chat."""

    def __init__(self, max_messages: int = 10, storage_path: str = "data/conversation.json"):
        self.max_messages = max_messages
        self.storage_path = Path(storage_path)
        self.messages: List[Dict] = []
        self._load()

    def _load(self) -> None:
        """Load conversation history from disk."""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.messages = data.get("messages", [])[-self.max_messages:]
            except Exception:
                self.messages = []

    def _save(self) -> None:
        """Save conversation history to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"messages": self.messages[-self.max_messages:]}
            self.storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def add_message(self, role: str, content: str) -> None:
        """Add a message to history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last N messages
        self.messages = self.messages[-self.max_messages:]
        self._save()

    def get_messages(self) -> List[Dict]:
        """Get recent messages for context."""
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self._save()


# Global instance per chat
_conversations: Dict[str, ConversationHistory] = {}


def get_conversation(chat_id: str = "default") -> ConversationHistory:
    """Get or create conversation history for a chat."""
    if chat_id not in _conversations:
        storage_path = f"data/conversation_{chat_id}.json"
        _conversations[chat_id] = ConversationHistory(storage_path=storage_path)
    return _conversations[chat_id]
