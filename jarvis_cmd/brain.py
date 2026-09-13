import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional
from jarvis_cmd.config import get_config
from jarvis_cmd.memory import get_all_facts

@dataclass
class Plan:
    intent: str
    command: Optional[str]
    reason: str
    source: str
    params: Optional[dict] = None

def get_system_prompt():
    facts = get_all_facts()
    facts_str = "\n- ".join(facts) if facts else "No facts known yet."
    return f"""You are Jarvis, an advanced offline AI assistant.
You can execute tasks by choosing the appropriate intent and parameters.
Return strict JSON only! Do not include markdown fences like ```json.
{{
  "intent": "execute|answer|schedule|memory_save|memory_delete|system|open_app",
  "command": "...",
  "reason": "..."
}}

Intents mapping:
- execute: Run Windows powershell/cmd command. Put command in "command".
- open_app: Open a program. Put app name (e.g. 'chrome', 'telegram') in "command".
- system: Media/System control. Put action ('volume_up', 'volume_down', 'mute', 'play_pause', 'next', 'prev') in "command".
- schedule: Schedule a task. Put "HH:MM|message" in "command" (e.g. "09:00|Wake up").
- memory_save: Save a fact about the user. Put the fact in "command".
- memory_delete: Delete a fact. Put the fact in "command".
- answer: Just talk to the user. Put your response in "reason", leave "command" empty.

User Facts:
- {facts_str}
"""

def _fallback_plan(user_text: str) -> Plan:
    text = user_text.strip().lower()
    if "громче" in text: return Plan("system", "volume_up", "Делаю громче", "fallback")
    if "тише" in text: return Plan("system", "volume_down", "Делаю тише", "fallback")
    if "пауз" in text: return Plan("system", "play_pause", "Пауза", "fallback")
    if text.startswith("открой "): return Plan("open_app", text.replace("открой ",""), "Открываю", "fallback")
    return Plan("answer", None, "Я в резервном режиме. Скажи 'открой [приложение]' или 'сделай громче'.", "fallback")

def _ollama_plan(user_text: str) -> Optional[Plan]:
    config = get_config()
    ollama_config = config.get_ollama_config()
    if not ollama_config.get("enabled", True): return None
    
    # Мы используем LocalModel, который маскируется под Ollama или запускается на порту 8080/11434
    url = ollama_config.get("url", "http://127.0.0.1:8080/v1/chat/completions")
    
    payload = {
        "model": "hermes",
        "messages": [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.1
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8")
            outer = json.loads(raw)
            # OpenAI API format for local model
            if "choices" in outer:
                body_str = outer["choices"][0]["message"]["content"]
            else:
                body_str = outer.get("response", "{}") # Fallback to ollama format
            
            # Clean up markdown JSON fences if model still outputs them
            body_str = body_str.replace("```json", "").replace("```", "").strip()
            body = json.loads(body_str)
            
            intent = str(body.get("intent", "answer")).strip()
            command = body.get("command")
            reason = str(body.get("reason", ""))
            return Plan(intent, command.strip() if isinstance(command, str) else None, reason, "local_model")
    except Exception as e:
        print(f"[Brain] Error: {e}")
        return None

def plan_command(user_text: str, conversation_history: Optional[list] = None) -> Plan:
    plan = _ollama_plan(user_text)
    if plan: return plan
    return _fallback_plan(user_text)