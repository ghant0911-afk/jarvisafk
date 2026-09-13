import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class Config:
    """Configuration manager for Jarvis."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            self._config = self._get_defaults()
            return

        config_file = Path(self.config_path)
        if not config_file.exists():
            self._config = self._get_defaults()
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except Exception:
            self._config = self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "logging": {
                "level": "INFO",
                "log_dir": "data/logs",
                "max_file_size_mb": 10,
                "backup_count": 5,
            },
            "safety": {
                "block_patterns": [
                    r"\bgit\s+reset\s+--hard\b",
                    r"\bgit\s+clean\s+-fd\b",
                    r"\bformat\s+[a-zA-Z]:\b",
                    r"\brd\s+/s\s+/q\b",
                    r"\bdel\s+/f\s+/s\s+/q\b",
                ],
                "ask_patterns": [
                    r"\brm\b",
                    r"\bdel\b",
                    r"\bmove\b",
                    r"\bren\b",
                    r"\bshutdown\b",
                    r"\brestart\b",
                    r"\btaskkill\b",
                    r"\bnpm\s+install\b",
                    r"\bpip\s+install\b",
                ],
            },
            "ollama": {
                "enabled": True,
                "model": "qwen2.5:7b",
                "url": "http://127.0.0.1:11434/api/generate",
                "timeout_sec": 8,
            },
            "history": {
                "path": "data/history.jsonl",
                "max_entries": 10000,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", self._get_defaults()["logging"])

    def get_safety_config(self) -> Dict[str, List[str]]:
        """Get safety configuration."""
        return self.get("safety", self._get_defaults()["safety"])

    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration."""
        config = self.get("ollama", self._get_defaults()["ollama"])
        # Override with environment variables if set
        config["model"] = os.getenv("JARVIS_OLLAMA_MODEL", config.get("model", "qwen2.5:7b"))
        config["url"] = os.getenv("JARVIS_OLLAMA_URL", config.get("url", "http://127.0.0.1:11434/api/generate"))
        return config

    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        config = self.get("telegram", {})
        # Override with environment variables
        config["bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN", config.get("bot_token", ""))
        config["chat_id"] = os.getenv("TELEGRAM_CHAT_ID", config.get("chat_id", ""))
        config["allow_execute"] = os.getenv("TELEGRAM_ALLOW_EXECUTE", str(config.get("allow_execute", True))).lower() == "true"
        config["poll_interval_sec"] = float(os.getenv("TELEGRAM_POLL_INTERVAL_SEC", config.get("poll_interval_sec", 1.5)))
        return config

    def get_history_path(self) -> str:
        """Get history file path."""
        return self.get("history.path", "data/history.jsonl")


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
