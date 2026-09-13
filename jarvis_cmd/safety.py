import re
from dataclasses import dataclass
from typing import List

from jarvis_cmd.config import get_config


def _get_patterns() -> tuple[List[str], List[str]]:
    """Get block and ask patterns from config."""
    config = get_config()
    safety_config = config.get_safety_config()
    return (
        safety_config.get("block_patterns", []),
        safety_config.get("ask_patterns", []),
    )


BLOCK_PATTERNS, ASK_PATTERNS = _get_patterns()


@dataclass
class SafetyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str


def check_command(command: str) -> SafetyDecision:
    cmd = command.strip().lower()
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, cmd):
            return SafetyDecision(False, False, "Команда заблокирована политикой безопасности.")
    for pattern in ASK_PATTERNS:
        if re.search(pattern, cmd):
            return SafetyDecision(True, True, "Команда потенциально рискованная, нужно подтверждение.")
    return SafetyDecision(True, False, "Команда безопасна для запуска.")
