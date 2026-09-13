"""
Jarvis Ultra UI  v4.0  вЂ”  Voice + GPT + Reminders
====================================================
вЂў Р“РѕР»РѕСЃРѕРІРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ (SpeechRecognition + pyaudio)
вЂў РќР°РїРѕРјРёРЅР°РЅРёСЏ СЃ РІСЃРїР»С‹РІР°СЋС‰РёРјРё СѓРІРµРґРѕРјР»РµРЅРёСЏРјРё
вЂў OpenAI GPT РёРЅС‚РµРіСЂР°С†РёСЏ С‡РµСЂРµР· API-РєР»СЋС‡
вЂў РСЃРїСЂР°РІР»РµРЅ Р±СЂР°СѓР·РµСЂ вЂ” РїРѕРёСЃРє РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ РІРЅСѓС‚СЂРё
вЂў РљРЅРѕРїРєР° РјРёРєСЂРѕС„РѕРЅР° РІ СЃС‚СЂРѕРєРµ РІРІРѕРґР°
"""
import sys
import os
import threading
import queue
import math
import random
import shutil
import subprocess
import json
import time
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk

sys.path.insert(0, str(Path(__file__).parent))

# в”Ђв”Ђ psutil в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False

# в”Ђв”Ђ sounddevice в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    import sounddevice as sd
    SD_OK = True
except ImportError:
    SD_OK = False

# в”Ђв”Ђ SpeechRecognition + numpy (Р·Р°РїРёСЃСЊ С‡РµСЂРµР· sounddevice, Р±РµР· pyaudio) в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    import speech_recognition as sr
    import numpy as np
    SR_OK = True
except ImportError:
    SR_OK = False
    np = None

# в”Ђв”Ђ openai в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    import openai
    OPENAI_OK = True
except ImportError:
    OPENAI_OK = False

# в”Ђв”Ђ plyer (СѓРІРµРґРѕРјР»РµРЅРёСЏ) в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    from plyer import notification as plyer_notify
    PLYER_OK = True
except ImportError:
    PLYER_OK = False

# subprocess for local model
import subprocess
import atexit
_LOCAL_SERVER_PROC = None

def _start_local_model():
    global _LOCAL_SERVER_PROC
    from pathlib import Path
    root_dir = Path(__file__).parent
    server_exe = root_dir / "LocalModel" / "llama-server.exe"
    model_file = root_dir / "LocalModel" / "tinyllama.gguf"
    if server_exe.exists() and model_file.exists() and _LOCAL_SERVER_PROC is None:
        try:
            # CREATE_NO_WINDOW = 0x08000000 on Windows
            log_f = open(root_dir / "LocalModel" / "llama_log.txt", "w")
            _LOCAL_SERVER_PROC = subprocess.Popen(
                [str(server_exe), "-m", str(model_file), "--port", "8080", "-c", "4096"],
                stdout=log_f, stderr=log_f, creationflags=0x08000000
            )
        except Exception:
            pass

def _stop_local_model():
    global _LOCAL_SERVER_PROC
    if _LOCAL_SERVER_PROC is not None:
        try:
            pid = _LOCAL_SERVER_PROC.pid
            _LOCAL_SERVER_PROC.kill()
            if PSUTIL_OK:
                import psutil
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    p.kill()
                except: pass
        except: pass
        _LOCAL_SERVER_PROC = None

    try:
        if PSUTIL_OK:
            import psutil
            for conn in psutil.net_connections():
                if conn.laddr.port == 8080 and conn.pid:
                    try: psutil.Process(conn.pid).kill()
                    except: pass
    except: pass

def ensure_local_server_ready(timeout=15, status_cb=None):
    import socket, urllib.request, time
    def _is_alive():
        try:
            urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=1)
            return True
        except:
            return False

    def _is_port_open():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', 8080)) == 0

    if _is_port_open():
        if _is_alive():
            return True
        else:
            if status_cb: status_cb("РћС‡РёСЃС‚РєР° Р·Р°РІРёСЃС€РµРіРѕ СЃРµСЂРІРµСЂР° (РїРѕСЂС‚ 8080)...")
            _stop_local_model()
            time.sleep(1)

    if status_cb: status_cb("Р—Р°РіСЂСѓР¶Р°СЋ Р»РѕРєР°Р»СЊРЅСѓСЋ РјРѕРґРµР»СЊвЂ¦")
    _start_local_model()
    
    start_t = time.time()
    while time.time() - start_t < timeout:
        if _is_alive():
            return True
        time.sleep(1)
    return False

atexit.register(_stop_local_model)

# в”Ђв”Ђ tkinterweb в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    from tkinterweb import HtmlFrame
    TKWEB_OK = True
except ImportError:
    TKWEB_OK = False

# в”Ђв”Ђ Jarvis modules в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
try:
    from jarvis_cmd.brain import plan_command
    from jarvis_cmd.executor import run_command
    from jarvis_cmd.safety import check_command
    from jarvis_cmd.actions import get_actions
    from jarvis_cmd.conversation import get_conversation
    from jarvis_cmd.memory import append_history
    from jarvis_cmd.scheduler import start_scheduler
    from jarvis_cmd.sound_player import SoundPlayer
    snd = SoundPlayer()
    JARVIS_OK = True
except Exception:
    JARVIS_OK = False


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  CONFIG
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
_CONFIG_PATH = (Path(sys.executable).parent / "jarvis_config.json"
                if getattr(sys, "frozen", False)
                else Path(__file__).parent / "jarvis_config.json")

def _load_config() -> dict:
    base = {
        "ai_api_key": "", "ai_base_url": "", "ai_model": "gpt-4o-mini",
        "default_city": "Moscow", "theme": "Cyan", "ai_volume": 100,
        "audio_out": "Default", "audio_in": "Default"
    }
    if _CONFIG_PATH.exists():
        try:
            base.update(json.loads(_CONFIG_PATH.read_text("utf-8")))
        except Exception:
            pass
    return base

def _save_config(cfg: dict):
    _CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), "utf-8")

def add_context_menu(widget):
    """Р”РѕР±Р°РІР»СЏРµС‚ РјРµРЅСЋ РїРѕ РїСЂР°РІРѕРјСѓ РєР»РёРєСѓ (Р’СЃС‚Р°РІРёС‚СЊ/РЎРєРѕРїРёСЂРѕРІР°С‚СЊ)."""
    menu = tk.Menu(widget, tearoff=0, bg="#0b1526", fg="#d8e8ff", activebackground="#00d4ff", bd=0)
    
    def _paste():
        try:
            text = widget.clipboard_get()
            widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass

    def _copy():
        if widget.select_present():
            widget.clipboard_clear()
            widget.clipboard_append(widget.selection_get())

    def _cut():
        if widget.select_present():
            _copy()
            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)

    menu.add_command(label="Р’СЃС‚Р°РІРёС‚СЊ", command=_paste)
    menu.add_command(label="РљРѕРїРёСЂРѕРІР°С‚СЊ", command=_copy)
    menu.add_command(label="Р’С‹СЂРµР·Р°С‚СЊ", command=_cut)
    menu.add_separator()
    menu.add_command(label="Р’С‹РґРµР»РёС‚СЊ РІСЃС‘", command=lambda: widget.select_range(0, tk.END))
    
    widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
    return widget

CONFIG = _load_config()

if CONFIG.get("ai_api_key"):
    os.environ["OPENAI_API_KEY"] = CONFIG["ai_api_key"]


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  COLOURS & THEME
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
BG      = "#050b15"
BG2     = "#07101d"
PANEL   = "#080f1c"
PANEL2  = "#0b1526"
BORDER  = "#13305a"
TEXT    = "#d8e8ff"
DIM     = "#5a7098"
BRIGHT  = "#ffffff"
BLUE    = "#3a7fff"
PURPLE  = "#8840e0"
PINK    = "#d040b8"
GREEN   = "#00df90"
AMBER   = "#ffaa00"
RED     = "#ff3060"
BUB_U   = "#0d2040"
BUB_J   = "#0a1830"
BRD_U   = "#2a68d0"

THEMES = {
    "Cyan":   {"accent": "#00d4ff", "hover": "#005060", "brd": "#0e1f3c"},
    "Purple": {"accent": "#b840e0", "hover": "#4a0860", "brd": "#1f0c2a"},
    "Green":  {"accent": "#00df90", "hover": "#005040", "brd": "#0a2618"},
    "Amber":  {"accent": "#ffaa00", "hover": "#604000", "brd": "#261a00"},
    "Red":    {"accent": "#ff3060", "hover": "#601020", "brd": "#2a0a10"},
}
THM  = THEMES.get(CONFIG.get("theme", "Cyan"), THEMES["Cyan"])
CYAN = THM["accent"]

INTENT_CLR = {
    "chat": PURPLE, "search": CYAN,  "weather": GREEN,
    "calendar": BLUE, "reminder": AMBER, "time": CYAN,
    "execute": PINK, "answer": DIM, "error": RED,
}
INTENT_ICO = {
    "chat": "рџ’¬", "search": "рџ”Ќ", "weather": "рџЊ¤",
    "calendar": "рџ“…", "reminder": "вЏ°", "time": "рџ•ђ",
    "execute": "вљЎ", "answer": "рџ’Ў", "error": "вќЊ",
}


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  REMINDER MANAGER
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class ReminderManager:
    """РњРµРЅРµРґР¶РµСЂ РЅР°РїРѕРјРёРЅР°РЅРёР№ СЃ СЃРёСЃС‚РµРјРЅС‹РјРё СѓРІРµРґРѕРјР»РµРЅРёСЏРјРё."""
    def __init__(self, on_remind=None):
        self._reminders = []          # list of (datetime, text)
        self._on_remind  = on_remind  # callback(text)
        self._lock       = threading.Lock()
        self._running    = True
        threading.Thread(target=self._loop, daemon=True).start()

    def add(self, text: str, when: datetime):
        with self._lock:
            self._reminders.append((when, text))
        return f"вЏ°  РќР°РїРѕРјРёРЅР°РЅРёРµ СѓСЃС‚Р°РЅРѕРІР»РµРЅРѕ: В«{text}В» РІ {when.strftime('%H:%M %d.%m')}"

    def parse_and_add(self, text: str) -> str:
        """РџР°СЂСЃРёС‚ СЃС‚СЂРѕРєСѓ РІРёРґР° 'РЅР°РїРѕРјРЅРё С‡РµСЂРµР· 5 РјРёРЅСѓС‚ РєСѓРїРёС‚СЊ РјРѕР»РѕРєРѕ'."""
        t = text.lower()
        now = datetime.now()
        delta = None
        # С‡РµСЂРµР· N РјРёРЅСѓС‚
        m = re.search(r"С‡РµСЂРµР·\s+(\d+)\s*(РјРёРЅ|С‡Р°СЃ)", t)
        if m:
            n = int(m.group(1))
            delta = timedelta(minutes=n) if "РјРёРЅ" in m.group(2) else timedelta(hours=n)
        # РІ HH:MM
        m2 = re.search(r"РІ\s+(\d{1,2}):(\d{2})", t)
        if m2 and not delta:
            h, mn = int(m2.group(1)), int(m2.group(2))
            target = now.replace(hour=h, minute=mn, second=0)
            if target <= now:
                target += timedelta(days=1)
            delta = target - now
        if delta is None:
            delta = timedelta(minutes=5)  # РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ 5 РјРёРЅ
        # РЈР±РёСЂР°РµРј СЃР»СѓР¶РµР±РЅС‹Рµ СЃР»РѕРІР°, РѕСЃС‚Р°РІР»СЏРµРј СЃСѓС‚СЊ
        remind_text = re.sub(r"(РЅР°РїРѕРјРЅРё|РЅР°РїРѕРјРёРЅР°РЅРёРµ|С‡РµСЂРµР·\s+\d+\s*\w+|РІ\s+\d+:\d+)", "", text, flags=re.IGNORECASE).strip()
        remind_text = remind_text or "РќР°РїРѕРјРёРЅР°РЅРёРµ!"
        when = now + delta
        return self.add(remind_text, when)

    def list_reminders(self) -> str:
        with self._lock:
            if not self._reminders:
                return "рџ“‹  РќРµС‚ Р°РєС‚РёРІРЅС‹С… РЅР°РїРѕРјРёРЅР°РЅРёР№."
            lines = ["рџ“‹  РђРєС‚РёРІРЅС‹Рµ РЅР°РїРѕРјРёРЅР°РЅРёСЏ:"]
            for i, (when, txt) in enumerate(sorted(self._reminders), 1):
                lines.append(f"  {i}. {when.strftime('%H:%M %d.%m')}  вЂ”  {txt}")
            return "\n".join(lines)

    def _loop(self):
        while self._running:
            now = datetime.now()
            triggered = []
            with self._lock:
                remaining = []
                for when, txt in self._reminders:
                    if now >= when:
                        triggered.append(txt)
                    else:
                        remaining.append((when, txt))
                self._reminders = remaining
            for txt in triggered:
                self._notify(txt)
            time.sleep(10)

    def _notify(self, text: str):
        if PLYER_OK:
            try:
                plyer_notify.notify(title="в—€  JARVIS РќР°РїРѕРјРёРЅР°РЅРёРµ", message=text, timeout=8)
            except Exception:
                pass
        if self._on_remind:
            self._on_remind(text)


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  VOICE CONTROLLER  (sounddevice + SpeechRecognition, Р±РµР· pyaudio)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class VoiceController:
    """Р“РѕР»РѕСЃРѕРІРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ С‡РµСЂРµР· sounddevice + Google Speech Recognition.
    РќРµ С‚СЂРµР±СѓРµС‚ pyaudio вЂ” РёСЃРїРѕР»СЊР·СѓРµС‚ СѓР¶Рµ СѓСЃС‚Р°РЅРѕРІР»РµРЅРЅС‹Р№ sounddevice."""
    SAMPLE_RATE = 16000
    DURATION    = 7       # РјР°РєСЃРёРјСѓРј СЃРµРєСѓРЅРґ Р·Р°РїРёСЃРё

    def __init__(self, on_text=None, on_state=None):
        self._on_text  = on_text
        self._on_state = on_state
        self._rec      = sr.Recognizer() if SR_OK else None

    @property
    def available(self):
        return SR_OK and SD_OK

    def listen_once(self):
        if not self.available:
            if self._on_state: self._on_state("error")
            return
        threading.Thread(target=self._listen_bg, daemon=True).start()

    def _listen_bg(self):
        if self._on_state: self._on_state("listening")
        try:
            # Р—Р°РїРёСЃС‹РІР°РµРј С‡РµСЂРµР· sounddevice (Р±РµР· pyaudio)
            frames = sd.rec(int(self.DURATION * self.SAMPLE_RATE),
                            samplerate=self.SAMPLE_RATE, channels=1,
                            dtype='int16')
            sd.wait()
            raw = frames.tobytes()
            # РћР±РѕСЂР°С‡РёРІР°РµРј РІ AudioData РґР»СЏ SpeechRecognition
            audio = sr.AudioData(raw, self.SAMPLE_RATE, 2)  # 2 Р±Р°Р№С‚Р° = int16
            if self._on_state: self._on_state("processing")
            text = self._rec.recognize_google(audio, language="ru-RU")
            if self._on_text:  self._on_text(text)
            if self._on_state: self._on_state("idle")
        except sr.UnknownValueError:
            if self._on_state: self._on_state("error")
        except Exception as exc:
            print(f"Voice error: {exc}")
            if self._on_state: self._on_state("error")


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  GPT CLIENT
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class GPTClient:
    """РЈРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Р№ РєР»РёРµРЅС‚ РґР»СЏ OpenAI, OpenRouter, LM Studio Рё Р»СЋР±С‹С… OpenAI-СЃРѕРІРјРµСЃС‚РёРјС‹С… API."""
    def __init__(self):
        self._history = []
        b = CONFIG.get("ai_base_url", "").strip() or None
        if b and ("localhost:8080" in b or "127.0.0.1:8080" in b):
            ensure_local_server_ready()

    def available(self) -> bool:
        k = CONFIG.get("ai_api_key", "").strip()
        b = CONFIG.get("ai_base_url", "").strip()
        return OPENAI_OK and (bool(k) or bool(b))

    def ask(self, text: str) -> str:
        if not self.available():
            return None
        try:
            b = CONFIG.get("ai_base_url", "").strip() or None
            k = CONFIG.get("ai_api_key", "").strip() or "local-key"
            m = CONFIG.get("ai_model", "").strip() or "gpt-4o-mini"
            if b and ("localhost:8080" in b or "127.0.0.1:8080" in b):
                if not ensure_local_server_ready():
                    return "вќЊ  РћС€РёР±РєР°: Р›РѕРєР°Р»СЊРЅС‹Р№ СЃРµСЂРІРµСЂ РЅРµ РѕС‚РІРµС‡Р°РµС‚."
            client = openai.OpenAI(api_key=k, base_url=b, timeout=15.0, default_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            self._history.append({"role": "user", "content": text})
            resp = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content":
                     "РўС‹ вЂ” СѓРјРЅС‹Р№ РР-Р°СЃСЃРёСЃС‚РµРЅС‚ JARVIS. РћС‚РІРµС‡Р°Р№ РєСЂР°С‚РєРѕ Рё РїРѕ РґРµР»Сѓ. "
                     "Р•СЃР»Рё РЅСѓР¶РЅРѕ, РёСЃРїРѕР»СЊР·СѓР№ СЌРјРѕРґР·Рё. РЇР·С‹Рє: СЂСѓСЃСЃРєРёР№."}
                ] + self._history[-20:],  # РїРѕСЃР»РµРґРЅРёРµ 20 СЃРѕРѕР±С‰РµРЅРёР№
                max_tokens=600,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content
            self._history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as exc:
            return f"вќЊ  GPT РѕС€РёР±РєР°: {exc}"

    def reset(self):
        self._history.clear()


GPT = GPTClient()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  DIRECT ACTIONS
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class DA:
    @staticmethod
    def show_processes() -> str:
        try:
            if PSUTIL_OK:
                procs = sorted(psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]),
                               key=lambda p: p.info["memory_percent"] or 0, reverse=True)[:18]
                lines = [f"{'PID':>7}  {'CPU%':>5}  {'RAM%':>5}  {'Name':<30}", "в”Ђ" * 56]
                for p in procs:
                    info = p.info
                    lines.append(f"{info['pid']:>7}  {info['cpu_percent'] or 0:>5.1f}  "
                                 f"{info['memory_percent'] or 0:>5.1f}  {(info['name'] or '')[:30]}")
                return "рџ’»  РџСЂРѕС†РµСЃСЃС‹ (С‚РѕРї 18 РїРѕ RAM):\n\n```\n" + "\n".join(lines) + "\n```"
            else:
                out = subprocess.check_output(["tasklist", "/fo", "table", "/nh"],
                                              text=True, errors="replace",
                                              creationflags=0x08000000, timeout=5)
                lines = [l for l in out.strip().splitlines() if l.strip()][:20]
                return "рџ’»  Р—Р°РїСѓС‰РµРЅРЅС‹Рµ РїСЂРѕС†РµСЃСЃС‹:\n\n```\n" + "\n".join(lines) + "\n```"
        except Exception as exc:
            return f"вќЊ  РџСЂРѕС†РµСЃСЃС‹: {exc}"

    @staticmethod
    def show_disk(drive: str = "D:") -> str:
        try:
            u = shutil.disk_usage(drive + "\\")
            total, free = u.total / 1073741824, u.free / 1073741824
            used = total - free
            pct  = used / total * 100
            bar  = "в–€" * int(pct / 5) + "в–‘" * (20 - int(pct / 5))
            return (f"рџ“Љ  Р”РёСЃРє {drive}\n\n  [{bar}]  {pct:.1f}%\n\n"
                    f"  Р’СЃРµРіРѕ:        {total:.1f} Р“Р‘\n"
                    f"  РСЃРїРѕР»СЊР·РѕРІР°РЅРѕ: {used:.1f} Р“Р‘\n"
                    f"  РЎРІРѕР±РѕРґРЅРѕ:     {free:.1f} Р“Р‘")
        except Exception as exc:
            return f"вќЊ  Р”РёСЃРє {drive}: {exc}"

    @staticmethod
    def show_dir(path: str = None) -> str:
        try:
            p = Path(path) if path else Path.cwd()
            items = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            dirs  = [f"рџ“Ѓ  {i.name}" for i in items if i.is_dir()][:10]
            files = [f"рџ“„  {i.name}" for i in items if i.is_file()][:12]
            return f"рџ“Ќ  {p}  ({len(dirs)} РїР°РїРѕРє, {len(files)} С„Р°Р№Р»РѕРІ)\n\n" + "\n".join(dirs + files)
        except Exception as exc:
            return f"вќЊ  {exc}"

    @staticmethod
    def get_weather(city: str) -> str:
        try:
            safe = urllib.parse.quote(city)
            req  = urllib.request.Request(f"https://wttr.in/{safe}?format=j1",
                                          headers={"User-Agent": "curl/7.64.1"})
            with urllib.request.urlopen(req, timeout=7) as r:
                data = json.loads(r.read().decode("utf-8"))
            cur   = data["current_condition"][0]
            wlist = data.get("weather", [])
            desc  = cur["weatherDesc"][0]["value"]
            result = (f"рџЊ¤  РџРѕРіРѕРґР° вЂ” {city}\n\n"
                      f"  РЎРµР№С‡Р°СЃ:    {cur['temp_C']}В°C  (РѕС‰СѓС‰Р°РµС‚СЃСЏ {cur['FeelsLikeC']}В°C)\n"
                      f"  РЎРѕСЃС‚РѕСЏРЅРёРµ: {desc}\n"
                      f"  Р’Р»Р°Р¶РЅРѕСЃС‚СЊ: {cur['humidity']}%  |  Р’РµС‚РµСЂ: {cur['windspeedKmph']} РєРј/С‡")
            if len(wlist) > 1:
                t = wlist[1]
                result += f"\n  Р—Р°РІС‚СЂР°:    {t.get('mintempC','?')}вЂ¦{t.get('maxtempC','?')}В°C"
            return result
        except Exception as exc:
            return f"вќЊ  РџРѕРіРѕРґР° РЅРµРґРѕСЃС‚СѓРїРЅР°: {exc}"


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  LOCAL PARSER
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class LocalParser:
    def __init__(self, city_fn=None, reminder_mgr=None, open_browser=None):
        self._city_fn     = city_fn
        self._rem         = reminder_mgr
        self._open_browser = open_browser  # callable(url)

    def parse(self, text: str, root=None) -> dict:
        t = text.lower()

        if any(w in t for w in ["РїСЂРѕС†РµСЃСЃ", "Р·Р°РїСѓС‰РµРЅ", "tasklist", "РїСЂРёР»РѕР¶РµРЅРё"]):
            return {"text": DA.show_processes(), "intent": "execute"}

        if any(w in t for w in ["РґРёСЃРє", "disk", "РјРµСЃС‚Рѕ", "СЃРІРѕР±РѕРґРЅ", "Р·Р°РЅСЏС‚Рѕ"]):
            drive = "D" if any(c in t for c in ["d:", "d ", "РґРёСЃРє d", "Рґ:"]) else "C"
            return {"text": DA.show_disk(drive + ":"), "intent": "execute"}

        if any(w in t for w in ["С„Р°Р№Р»", "РїР°РїРє", "РґРёСЂРµРєС‚РѕСЂ", "ls", "dir", "СЃРѕРґРµСЂР¶РёРј"]):
            return {"text": DA.show_dir(), "intent": "execute"}

        if any(w in t for w in ["РїРѕРіРѕРґР°", "weather", "С‚РµРјРїРµСЂР°С‚СѓСЂ", "РґРѕР¶РґСЊ", "РІРµС‚РµСЂ"]):
            city = (self._city_fn() if self._city_fn else None) or "Moscow"
            return {"text": DA.get_weather(city), "intent": "weather"}

        if any(w in t for w in ["С‡Р°СЃ", "РІСЂРµРјСЏ", "РґР°С‚Р°", "date", "time", "С‡РёСЃР»Рѕ", "СЃРµРіРѕРґРЅСЏ"]):
            if root:
                root.after(0, lambda: TimePopup(root))
            now  = datetime.now()
            days = ["РџРѕРЅРµРґРµР»СЊРЅРёРє","Р’С‚РѕСЂРЅРёРє","РЎСЂРµРґР°","Р§РµС‚РІРµСЂРі","РџСЏС‚РЅРёС†Р°","РЎСѓР±Р±РѕС‚Р°","Р’РѕСЃРєСЂРµСЃРµРЅСЊРµ"]
            return {"text": (f"рџ•ђ  {now.strftime('%H:%M:%S')}\n"
                             f"рџ“…  {now.strftime('%d %B %Y')}\n"
                             f"рџ“†  {days[now.weekday()]}"), "intent": "time"}

        # РќР°РїРѕРјРёРЅР°РЅРёСЏ
        if any(w in t for w in ["РЅР°РїРѕРјРЅРё", "РЅР°РїРѕРјРёРЅР°РЅРёРµ", "reminder"]):
            if self._rem:
                return {"text": self._rem.parse_and_add(text), "intent": "reminder"}
            return {"text": "вљ пёЏ  РњРµРЅРµРґР¶РµСЂ РЅР°РїРѕРјРёРЅР°РЅРёР№ РЅРµ РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ.", "intent": "error"}

        if any(w in t for w in ["РјРѕРё РЅР°РїРѕРјРёРЅР°РЅРёСЏ", "СЃРїРёСЃРѕРє РЅР°РїРѕРјРёРЅР°РЅРёР№", "РЅР°РїРѕРјРёРЅР°РЅРёСЏ"]):
            if self._rem:
                return {"text": self._rem.list_reminders(), "intent": "reminder"}

        if any(w in t for w in ["notepad", "Р±Р»РѕРєРЅРѕС‚"]):
            subprocess.Popen(["notepad"])
            return {"text": "рџ“ќ  Р‘Р»РѕРєРЅРѕС‚ РѕС‚РєСЂС‹С‚.", "intent": "execute"}

        if any(w in t for w in ["calc", "РєР°Р»СЊРєСѓР»"]):
            subprocess.Popen(["calc"])
            return {"text": "рџ–©  РљР°Р»СЊРєСѓР»СЏС‚РѕСЂ РѕС‚РєСЂС‹С‚.", "intent": "execute"}

        if any(w in t for w in ["РїСЂРѕРІРѕРґРЅРёРє", "explorer"]):
            subprocess.Popen(["explorer", "D:\\Jarvis"])
            return {"text": "рџ“Ѓ  РџСЂРѕРІРѕРґРЅРёРє РѕС‚РєСЂС‹С‚ в†’ D:\\Jarvis", "intent": "execute"}

        # РџРѕРёСЃРє вЂ” РІСЃРµРіРґР° РІРѕ РІРЅСѓС‚СЂРµРЅРЅРµРј Р±СЂР°СѓР·РµСЂРµ
        if any(w in t for w in ["РЅР°Р№РґРё", "РЅР°Р№С‚Рё", "РїРѕРіСѓРіР»Рё", "Р·Р°РіСѓРіР»Рё", "search", "РїРѕРёСЃРє"]):
            query = text
            for prefix in ["РЅР°Р№РґРё ", "РЅР°Р№С‚Рё ", "РїРѕРіСѓРіР»Рё ", "Р·Р°РіСѓРіР»Рё ", "РїРѕРёСЃРє ", "search "]:
                if t.startswith(prefix):
                    query = text[len(prefix):]
                    break
            url = "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(query)
            if self._open_browser and root:
                root.after(0, lambda u=url: self._open_browser(u))
            return {"text": f"рџ”Ќ  РС‰Сѓ РІРѕ РІРЅСѓС‚СЂРµРЅРЅРµРј Р±СЂР°СѓР·РµСЂРµ:\nВ«{query}В»", "intent": "search"}

        if any(w in t for w in ["РїСЂРёРІРµС‚", "hello", "hi", "Р·РґСЂР°РІСЃС‚РІСѓР№"]):
            gpt_hint = "AI РіРѕС‚РѕРІ." if GPT.available() else "Р’РІРµРґРё API-РєР»СЋС‡ РёР»Рё Base URL РІ вљ™ РќР°СЃС‚СЂРѕР№РєРё в†’ AI & Web."
            return {"text": f"РџСЂРёРІРµС‚, Commander! рџ‘‹\n{gpt_hint}", "intent": "chat"}

        return None  # РЅРµС‚ РјР°С‚С‡Р° в†’ РёРґС‘Рј РІ GPT/AI


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  ANIMATED BACKGROUND
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class StarField(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, highlightthickness=0, bd=0, bg=BG, **kw)
        self.ph = 0.0
        self._W = self._H = 0
        self._stars = [
            dict(x=random.random(), y=random.random(),
                 s=random.uniform(0.8, 2.2), v=random.uniform(6e-5, 1.8e-4),
                 c=random.choice(["#ffffff", "#90bfff", "#c0a0ff", "#50d8ff"]))
            for _ in range(90)
        ]
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, evt):
        self._W, self._H = evt.width, evt.height
        self._draw()

    def _draw_grid(self, W, H):
        sp, off = 66, int(self.ph * 10 % 66)
        for x in range(-sp, W + sp, sp):
            self.create_line(x + off, 0, x + off, H, fill="#081b3c", width=1)
        for y in range(-sp, H + sp, sp):
            self.create_line(0, y + off, W, y + off, fill="#081b3c", width=1)

    def _draw_glows(self, W, H):
        dx = int(18 * math.sin(self.ph * 0.010))
        dy = int(12 * math.cos(self.ph * 0.013))
        self.create_oval(W-500+dx, -200+dy, W+160+dx, 400+dy, fill="#071848", outline="")
        self.create_oval(-200-dx, H-420+dy, 440-dx, H+200+dy, fill="#130838", outline="")

    def _draw_stars(self, W, H):
        for s in self._stars:
            s["y"] -= s["v"]
            if s["y"] < -0.01:
                s["y"] = 1.02
                s["x"] = random.random()
            px, py = s["x"] * W, s["y"] * H
            r = s["s"] * (0.7 + 0.3 * math.sin(self.ph * 0.06 + px * 0.02))
            self.create_oval(px-r, py-r, px+r, py+r, fill=s["c"], outline="")

    def _draw_hologram(self, W, H):
        cx, cy, ph, N = W * 0.79, H * 0.35, self.ph, 72
        for rx, ry, vel, ph0, color, lw in [
            (158, 56,  0.010, 0.0,            "#2a68d8", 2),
            (140,  6, -0.017, math.pi/2,      "#6028b8", 1),
            (148, 84,  0.025, math.pi/4,      "#00a8c8", 1),
            (124, 30, -0.014, 3*math.pi/4,    "#b028a8", 1),
        ]:
            ang = ph * vel + ph0
            ca, sa = math.cos(ang), math.sin(ang)
            pts = []
            for i in range(N):
                t = 2 * math.pi * i / N
                ex, ey = rx * math.cos(t), ry * math.sin(t)
                pts.extend([cx + ex*ca - ey*sa, cy + ex*sa + ey*ca])
            pts.extend(pts[:2])
            self.create_line(pts, fill=color, width=lw, smooth=True)

        for i in range(9):
            a = ph * 0.022 + i * 2 * math.pi / 9
            px, py = cx + 162*math.cos(a), cy + 162*0.36*math.sin(a)
            s = 1.5 + 0.8 * abs(math.sin(a + ph * 0.08))
            self.create_oval(px-s, py-s, px+s, py+s, fill=CYAN, outline="")

        for i in range(6):
            a = ph * (-0.030) + i * 2 * math.pi / 6
            px, py = cx + 140*math.cos(a), cy + 140*0.58*math.sin(a)
            self.create_oval(px-2, py-2, px+2, py+2, fill=PURPLE, outline="")

        cr = 14 + 6 * math.sin(ph * 0.06)
        self.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, outline=CYAN, fill=BG, width=2)
        self.create_oval(cx-4, cy-4, cx+4, cy+4, fill=CYAN, outline="")

        for i in range(6):
            ang = ph * 0.028 * (-1 if i%2 else 1) + i * math.pi/3
            self.create_line(cx+18*math.cos(ang), cy+18*math.sin(ang),
                             cx+56*math.cos(ang), cy+56*math.sin(ang), fill="#1a4a90", width=1)

        for i in range(3):
            start = int(math.degrees(ph * 0.018 * (1 if i%2 else -1) + i * 2.2))
            self.create_arc(cx-76, cy-30, cx+76, cy+30, start=start, extent=55+i*18,
                            style=tk.ARC, outline=["#1a5090","#401880","#006070"][i], width=1)

        sy = cy - 92 + (ph * 1.8 % 184)
        self.create_line(cx-174, sy, cx+174, sy, fill="#006060", width=1)

    def _draw(self):
        self.delete("all")
        W = max(self._W or self.winfo_width(), 1)
        H = max(self._H or self.winfo_height(), 1)
        self._draw_glows(W, H)
        self._draw_grid(W, H)
        self._draw_stars(W, H)
        self._draw_hologram(W, H)

    def tick(self):
        self.ph += 1.0
        self._draw()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  CHAT AREA
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class ChatArea(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG2, **kw)
        cv = tk.Canvas(self, bg=BG2, highlightthickness=0, bd=0)
        sb = tk.Scrollbar(self, orient="vertical", command=cv.yview,
                          bg=PANEL, troughcolor=BG2, relief=tk.FLAT)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._cv    = cv
        self._inner = tk.Frame(cv, bg=BG2)
        self._win   = cv.create_window((0, 0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>", lambda _: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(self._win, width=e.width))
        cv.bind_all("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _end(self):
        self._cv.after(60, lambda: self._cv.yview_moveto(1.0))

    def add_system(self, msg: str):
        f = tk.Frame(self._inner, bg=BG2, pady=3)
        f.pack(fill=tk.X)
        tk.Label(f, text=f"в”Ђв”Ђ {msg} в”Ђв”Ђ", fg="#2a4a70", bg=BG2, font=("Segoe UI", 8, "italic")).pack()
        self._end()

    def add_user(self, msg: str):
        ts  = datetime.now().strftime("%H:%M")
        row = tk.Frame(self._inner, bg=BG2, pady=7, padx=12)
        row.pack(fill=tk.X)
        bub = tk.Frame(row, bg=BUB_U, highlightthickness=1, highlightbackground=BRD_U, padx=16, pady=10)
        bub.pack(side=tk.RIGHT)
        tk.Label(bub, text="рџ‘¤  YOU", fg=BLUE, bg=BUB_U, font=("Consolas", 8, "bold")).pack(anchor="e")
        tk.Frame(bub, bg=BRD_U, height=1).pack(fill=tk.X, pady=(2, 5))
        tk.Label(bub, text=msg, fg=TEXT, bg=BUB_U, font=("Segoe UI", 11), wraplength=540, justify=tk.RIGHT).pack(anchor="e")
        tk.Label(bub, text=ts, fg=DIM, bg=BUB_U, font=("Segoe UI", 8)).pack(anchor="e", pady=(3, 0))
        self._end()

    def add_jarvis(self, text: str = "", intent: str = "chat") -> dict:
        ts    = datetime.now().strftime("%H:%M")
        color = INTENT_CLR.get(intent, PURPLE)
        icon  = INTENT_ICO.get(intent, "рџ¤–")
        row   = tk.Frame(self._inner, bg=BG2, pady=7, padx=12)
        row.pack(fill=tk.X)
        ico   = tk.Label(row, text=icon, bg=BG2, fg=color, font=("Segoe UI", 20))
        ico.pack(side=tk.LEFT, anchor="n", padx=(0, 8))
        bub   = tk.Frame(row, bg=BUB_J, highlightthickness=1, highlightbackground=color, padx=16, pady=10)
        bub.pack(side=tk.LEFT, fill=tk.X, expand=False)
        hdr   = tk.Frame(bub, bg=BUB_J)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="JARVIS", fg=color, bg=BUB_J, font=("Consolas", 8, "bold")).pack(side=tk.LEFT)
        ilbl  = tk.Label(hdr, text=f"  в–ё  {intent.upper()}", fg=DIM, bg=BUB_J, font=("Segoe UI", 8))
        ilbl.pack(side=tk.LEFT)
        abar  = tk.Frame(bub, bg=color, height=1)
        abar.pack(fill=tk.X, pady=(3, 6))
        tv    = tk.StringVar(value=text)
        tk.Label(bub, textvariable=tv, fg=TEXT, bg=BUB_J, font=("Segoe UI", 11), wraplength=540, justify=tk.LEFT).pack(anchor="w")
        tk.Label(bub, text=ts, fg=DIM, bg=BUB_J, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self._end()
        return dict(tv=tv, bub=bub, ilbl=ilbl, abar=abar, ico=ico)

    def update_bubble(self, refs: dict, text: str, intent: str):
        color = INTENT_CLR.get(intent, PURPLE)
        refs["tv"].set(text)
        refs["ilbl"].config(text=f"  в–ё  {intent.upper()}")
        refs["abar"].config(bg=color)
        refs["bub"].config(highlightbackground=color)
        refs["ico"].config(text=INTENT_ICO.get(intent, "рџ¤–"), fg=color)
        self._end()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  TIME POPUP
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class TimePopup:
    _inst = None
    def __new__(cls, parent):
        try:
            if cls._inst and cls._inst.win.winfo_exists():
                cls._inst.win.lift(); cls._inst.win.focus()
                return cls._inst
        except Exception: pass
        obj = super().__new__(cls); cls._inst = obj; return obj

    def __init__(self, parent):
        if hasattr(self, "_ok"): return
        self._ok = True
        self.win = tk.Toplevel(parent)
        self.win.title("в—€  Time")
        self.win.geometry("300x178+80+80")
        self.win.resizable(False, False)
        self.win.configure(bg=BG)
        self.win.attributes("-topmost", True)
        outer = tk.Frame(self.win, bg=CYAN, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill=tk.BOTH, expand=True)
        tk.Label(inner, text="в—€  Р’Р Р•РњРЇ Р Р”РђРўРђ", fg=CYAN, bg=PANEL, font=("Consolas", 9, "bold")).pack(pady=(10, 2))
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X, padx=14)
        self._tv = tk.StringVar(); self._dv = tk.StringVar(); self._wv = tk.StringVar()
        tk.Label(inner, textvariable=self._tv, fg=CYAN, bg=PANEL, font=("Consolas", 38, "bold")).pack(pady=(6, 0))
        tk.Label(inner, textvariable=self._dv, fg=TEXT, bg=PANEL, font=("Segoe UI", 12)).pack()
        tk.Label(inner, textvariable=self._wv, fg=DIM, bg=PANEL, font=("Segoe UI", 9)).pack(pady=(0, 4))
        tk.Button(inner, text="вњ–", command=self._close, bg=PANEL, fg=DIM, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 9), cursor="hand2").pack(pady=(0, 8))
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self._tick()

    def _tick(self):
        try:
            if not self.win.winfo_exists(): return
        except Exception: return
        n = datetime.now()
        self._tv.set(n.strftime("%H:%M:%S"))
        self._dv.set(n.strftime("%d %B %Y"))
        self._wv.set(["РџРЅ","Р’С‚","РЎСЂ","Р§С‚","РџС‚","РЎР±","Р’СЃ"][n.weekday()])
        self.win.after(1000, self._tick)

    def _close(self):
        TimePopup._inst = None; self.win.destroy()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  INTERNAL BROWSER (СЃС‚СЂРѕРіРѕ Р±РµР· РІРЅРµС€РЅРёС… РѕС‚РєСЂС‹С‚РёР№)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class BrowserWindow:
    def __init__(self, parent, url: str = "https://lite.duckduckgo.com/lite/"):
        self.win = tk.Toplevel(parent)
        self.win.title("в—€  JARVIS Internal Browser")
        self.win.geometry("1280x820")
        self.win.configure(bg=BG)
        self._frame = None

        nav = tk.Frame(self.win, bg=PANEL)
        nav.pack(fill=tk.X)
        nav.grid_columnconfigure(3, weight=1)

        for col, (txt, fn) in enumerate([("в—Ђ", self._back), ("в–¶", self._forward), ("вџі", self._reload)]):
            tk.Button(nav, text=txt, command=fn, bg="#0c1830", fg=CYAN,
                      activebackground="#1a3060", relief=tk.FLAT, bd=0,
                      font=("Segoe UI", 13), cursor="hand2", padx=12, pady=7).grid(row=0, column=col, padx=2, pady=6)

        uw = tk.Frame(nav, bg=BLUE, padx=1, pady=1)
        uw.grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=6)
        self._url_var = tk.StringVar(value=url)
        ue = tk.Entry(uw, textvariable=self._url_var, bg="#060d1e", fg=TEXT,
                      insertbackground=CYAN, relief=tk.FLAT, font=("Segoe UI", 11))
        add_context_menu(ue)
        ue.pack(fill=tk.X, ipady=8, padx=1, pady=1)
        ue.bind("<Return>", lambda _: self._go(self._url_var.get()))

        tk.Button(nav, text="GO", command=lambda: self._go(self._url_var.get()),
                  bg="#1040a0", fg=BRIGHT, activebackground="#2060d0",
                  relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"),
                  cursor="hand2", padx=16, pady=8).grid(row=0, column=4, padx=(8, 8), pady=6)

        tk.Frame(self.win, bg=BORDER, height=1).pack(fill=tk.X)

        if TKWEB_OK:
            self._frame = HtmlFrame(self.win, messages_enabled=False)
            self._frame.pack(fill=tk.BOTH, expand=True)
            self._frame.load_url(url)
        else:
            info = tk.Frame(self.win, bg=BG2)
            info.pack(fill=tk.BOTH, expand=True)
            tk.Label(info, text="рџЊђ", fg=RED, bg=BG2, font=("Segoe UI", 52)).pack(pady=(50, 8))
            tk.Label(info, text="РЈСЃС‚Р°РЅРѕРІРё tkinterweb:", fg=TEXT, bg=BG2, font=("Consolas", 14, "bold")).pack()
            tk.Label(info, text="python -m pip install tkinterweb", fg=GREEN, bg=BG2, font=("Consolas", 11)).pack(pady=(8, 0))

    def _go(self, url: str):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self._url_var.set(url)
        if TKWEB_OK and self._frame:
            self._frame.load_url(url)

    def _back(self):
        if TKWEB_OK and self._frame: self._frame.go_back()

    def _forward(self):
        if TKWEB_OK and self._frame: self._frame.go_forward()

    def _reload(self):
        if TKWEB_OK and self._frame: self._frame.load_url(self._url_var.get())


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  SETTINGS WINDOW
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class SettingsWindow:
    def __init__(self, parent, config: dict, on_save=None):
        self.win = tk.Toplevel(parent)
        self._cfg = config.copy()
        self._on_save = on_save
        self._vars = {}
        self.win.title("в—€  JARVIS Settings")
        self.win.geometry("660x560+150+100")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)

        self.out_devs = ["Default"]
        self.in_devs  = ["Default"]
        if SD_OK:
            try:
                devs = sd.query_devices()
                self.out_devs += [d['name'] for d in devs if d['max_output_channels'] > 0]
                self.in_devs  += [d['name'] for d in devs if d['max_input_channels'] > 0]
            except Exception: pass

        self._build()

    def _build(self):
        outer = tk.Frame(self.win, bg=CYAN, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill=tk.BOTH, expand=True)
        tk.Label(inner, text="в—€  JARVIS SETTINGS", fg=CYAN, bg=PANEL, font=("Consolas", 14, "bold")).pack(pady=(16, 2), padx=22, anchor="w")
        tk.Label(inner, text="System Configuration", fg=DIM, bg=PANEL, font=("Segoe UI", 9)).pack(padx=22, anchor="w")
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=(8, 0))

        area = tk.Frame(inner, bg=PANEL)
        area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.nav = tk.Frame(area, bg=PANEL2, width=160)
        self.nav.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.content = tk.Frame(area, bg=PANEL)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tabs = {}
        self._add_tab("рџ¤–  AI & Web",    self._tab_ai)
        self._add_tab("рџ”Љ  РђСѓРґРёРѕ",       self._tab_audio)
        self._add_tab("рџЋЁ  РРЅС‚РµСЂС„РµР№СЃ",   self._tab_theme)
        self._switch("рџ¤–  AI & Web")

        br = tk.Frame(inner, bg=PANEL)
        br.pack(pady=(0, 18), side=tk.BOTTOM)
        tk.Button(br, text="рџ’ѕ  РЎРѕС…СЂР°РЅРёС‚СЊ", command=self._save, bg="#104080", fg=BRIGHT, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 10, "bold"), cursor="hand2", padx=22, pady=10).pack(side=tk.LEFT, padx=6)
        tk.Button(br, text="вњ–  РћС‚РјРµРЅР°", command=self.win.destroy, bg="#200818", fg=DIM, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 10), cursor="hand2", padx=22, pady=10).pack(side=tk.LEFT, padx=6)

    def _add_tab(self, name, fn):
        btn = tk.Button(self.nav, text=name, bg=PANEL2, fg=DIM, relief=tk.FLAT, bd=0, anchor="w",
                        font=("Segoe UI", 10), cursor="hand2", padx=12, pady=10,
                        command=lambda n=name: self._switch(n))
        btn.pack(fill=tk.X)
        frame = tk.Frame(self.content, bg=PANEL)
        fn(frame)
        self.tabs[name] = {"btn": btn, "frame": frame}

    def _switch(self, name):
        for n, t in self.tabs.items():
            t["frame"].pack_forget()
            t["btn"].config(bg=PANEL2, fg=DIM)
        self.tabs[name]["frame"].pack(fill=tk.BOTH, expand=True)
        self.tabs[name]["btn"].config(bg=BORDER, fg=CYAN)

    def _tab_ai(self, p):
        self._sec(p, "в—€  РЈРЅРёРІРµСЂСЃР°Р»СЊРЅР°СЏ РР-РњРѕРґРµР»СЊ", GREEN)
        self._field(p, "ai_api_key", "API РљР»СЋС‡ (sk-...) [РґР»СЏ Р»РѕРєР°Р»СЊРЅС‹С… РјРѕР¶РЅРѕ Р»СЋР±РѕРµ]", show="*")
        self._field(p, "ai_base_url", "Base URL (РїСѓСЃС‚Рѕ = OpenAI)", hint="OpenRouter: https://openrouter.ai/api/v1  |  Р›РѕРєР°Р»СЊРЅРѕ: http://localhost:1234/v1")
        self._field(p, "ai_model", "РњРѕРґРµР»СЊ", hint="РќР°РїСЂРёРјРµСЂ: gpt-4o-mini, llama-3, deepseek-coder")
        
        check_f = tk.Frame(p, bg=PANEL)
        check_f.pack(fill=tk.X, pady=(4, 0))
        self._check_lbl = tk.Label(check_f, text="", fg=DIM, bg=PANEL, font=("Segoe UI", 8))
        self._check_lbl.pack(side=tk.LEFT)
        tk.Button(check_f, text="вњ”  РџСЂРѕРІРµСЂРёС‚СЊ РїРѕРґРєР»СЋС‡РµРЅРёРµ", command=self._check_gpt,
                  bg="#0a3020", fg=GREEN, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 8, "bold"), cursor="hand2", padx=10, pady=4).pack(side=tk.RIGHT)
                  
        local_f = tk.Frame(p, bg=PANEL)
        local_f.pack(fill=tk.X, pady=(15, 0))
        tk.Button(local_f, text="рџ’» Р’РєР»СЋС‡РёС‚СЊ Р›РѕРєР°Р»СЊРЅСѓСЋ РћС„Р»Р°Р№РЅ РњРѕРґРµР»СЊ (1-click)", command=self._enable_local_model,
                  bg="#1a4060", fg=CYAN, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 8, "bold"), cursor="hand2", padx=10, pady=4).pack(side=tk.RIGHT)

        self._sec(p, "в—€  РџРѕРіРѕРґР°", AMBER)
        self._field(p, "default_city", "Р“РѕСЂРѕРґ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ", hint="Moscow")

    def _check_gpt(self):
        k = self._vars.get("ai_api_key", tk.StringVar()).get().strip() or "local"
        b = self._vars.get("ai_base_url", tk.StringVar()).get().strip() or None
        m = self._vars.get("ai_model", tk.StringVar()).get().strip() or "gpt-4o-mini"
        
        self._check_lbl.config(text="вЏі РџРѕРґРєР»СЋС‡Р°СЋСЃСЊвЂ¦", fg=DIM)
        def _do():
            if b and ("localhost:8080" in b or "127.0.0.1:8080" in b):
                if not ensure_local_server_ready(status_cb=lambda txt: self.win.after(0, lambda: self._check_lbl.config(text=f"вЏі {txt}", fg=DIM))):
                    self.win.after(0, lambda: self._check_lbl.config(text="вќЊ  РћС€РёР±РєР°: Р›РѕРєР°Р»СЊРЅС‹Р№ СЃРµСЂРІРµСЂ РЅРµ Р·Р°РїСѓСЃС‚РёР»СЃСЏ", fg=RED))
                    return

            try:
                cl = openai.OpenAI(api_key=k, base_url=b, timeout=5.0, default_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
                cl.chat.completions.create(model=m,
                    messages=[{"role":"user","content":"ping"}], max_tokens=2)
                self.win.after(0, lambda: self._check_lbl.config(text="вњ…  РЈСЃРїРµС€РЅРѕ РїРѕРґРєР»СЋС‡РµРЅРѕ!", fg=GREEN))
            except Exception as exc:
                err = str(exc).replace("\n", " ")
                self.win.after(0, lambda text=err: self._check_lbl.config(text=f"вќЊ  {text[:100]}", fg=RED))
        threading.Thread(target=_do, daemon=True).start()

    def _enable_local_model(self):
        self._vars.get("ai_api_key", tk.StringVar()).set("local")
        self._vars.get("ai_base_url", tk.StringVar()).set("http://127.0.0.1:8080/v1")
        self._vars.get("ai_model", tk.StringVar()).set("tinyllama")
        
        self._check_lbl.config(text="вЏі Р—Р°РїСѓСЃРє Р»РѕРєР°Р»СЊРЅРѕРіРѕ СЃРµСЂРІРµСЂР°вЂ¦", fg=DIM)
        def _start_and_check():
            ensure_local_server_ready(status_cb=lambda txt: self.win.after(0, lambda: self._check_lbl.config(text=f"вЏі {txt}", fg=DIM)))
            self.win.after(0, self._check_gpt)
        threading.Thread(target=_start_and_check, daemon=True).start()

    def _tab_audio(self, p):
        self._sec(p, "в—€  Р“СЂРѕРјРєРѕСЃС‚СЊ AI", BLUE)
        v = tk.IntVar(value=self._cfg.get("ai_volume", 100))
        self._vars["ai_volume"] = v
        lbl = tk.Label(p, text=f"{v.get()}%", fg=CYAN, bg=PANEL, font=("Consolas", 10))
        lbl.pack(anchor="w")
        tk.Scale(p, from_=0, to=100, orient=tk.HORIZONTAL, variable=v, bg=PANEL, fg=TEXT,
                 highlightthickness=0, bd=0, troughcolor=BG2, activebackground=CYAN,
                 command=lambda val: lbl.config(text=f"{val}%")).pack(fill=tk.X, pady=(5, 15))
        self._sec(p, "в—€  РЈСЃС‚СЂРѕР№СЃС‚РІР°", PINK)
        self._dropdown(p, "audio_out", "Р’С‹РІРѕРґ (Р”РёРЅР°РјРёРєРё)", self.out_devs)
        self._dropdown(p, "audio_in",  "Р’РІРѕРґ (РњРёРєСЂРѕС„РѕРЅ)",  self.in_devs)

    def _tab_theme(self, p):
        self._sec(p, "в—€  РўРµРјР° РёРЅС‚РµСЂС„РµР№СЃР°", CYAN)
        var = tk.StringVar(value=self._cfg.get("theme", "Cyan"))
        self._vars["theme"] = var
        for tname, tvals in THEMES.items():
            f = tk.Frame(p, bg=PANEL)
            f.pack(fill=tk.X, pady=3)
            tk.Frame(f, bg=tvals["accent"], width=18, height=18).pack(side=tk.LEFT, padx=(0, 10))
            tk.Radiobutton(f, text=f"{tname}", variable=var, value=tname, fg=TEXT, bg=PANEL,
                           selectcolor=tvals["brd"], activebackground=PANEL, font=("Segoe UI", 11),
                           bd=0, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, anchor="w")

    def _sec(self, parent, title, color):
        f = tk.Frame(parent, bg=PANEL)
        f.pack(fill=tk.X, pady=(14, 4))
        tk.Frame(f, bg=color, width=3, height=18).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(f, text=title, fg=color, bg=PANEL, font=("Consolas", 9, "bold")).pack(side=tk.LEFT, anchor="w")

    def _field(self, parent, key, label, show="", hint=""):
        tk.Label(parent, text=label, fg=DIM, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w")
        wrap = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrap.pack(fill=tk.X, pady=(2, 0))
        var = tk.StringVar(value=self._cfg.get(key, ""))
        entry = tk.Entry(wrap, textvariable=var, bg="#060d1e", fg=TEXT, insertbackground=CYAN,
                         relief=tk.FLAT, font=("Segoe UI", 11), show=show, highlightthickness=0)
        add_context_menu(entry)
        entry.pack(fill=tk.X, ipady=9, padx=1, pady=1)
        if hint:
            tk.Label(parent, text=hint, fg="#2a4060", bg=PANEL, font=("Segoe UI", 7)).pack(anchor="w", pady=(1, 0))
        self._vars[key] = var

    def _dropdown(self, parent, key, label, options):
        tk.Label(parent, text=label, fg=DIM, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 2))
        var = tk.StringVar(value=self._cfg.get(key, options[0] if options else ""))
        ttk.Combobox(parent, textvariable=var, values=options, state="readonly").pack(fill=tk.X, ipady=4)
        self._vars[key] = var

    def _save(self):
        for key, var in self._vars.items():
            self._cfg[key] = int(var.get()) if isinstance(var, tk.IntVar) else var.get().strip()
        _save_config(self._cfg)
        k = self._cfg.get("ai_api_key", "")
        if k: os.environ["OPENAI_API_KEY"] = k
        if self._on_save: self._on_save(self._cfg)
        messagebox.showinfo("Settings", "вњ“  РЎРѕС…СЂР°РЅРµРЅРѕ!\n\nРР·РјРµРЅРµРЅРёСЏ С‚РµРјС‹ РїСЂРёРјРµРЅСЏС‚СЃСЏ РїРѕСЃР»Рµ РїРµСЂРµР·Р°РїСѓСЃРєР°.")
        self.win.destroy()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  SEARCH POPUP
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class SearchPopup:
    def __init__(self, parent, on_search):
        self.win = tk.Toplevel(parent)
        self.win.title("в—€  РџРѕРёСЃРє")
        self.win.geometry("500x130+200+200")
        self.win.resizable(False, False)
        self.win.configure(bg=BG)
        self.win.attributes("-topmost", True)
        outer = tk.Frame(self.win, bg=CYAN, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        tk.Label(inner, text="рџ”Ќ  РџРѕРёСЃРє РІ РёРЅС‚РµСЂРЅРµС‚Рµ", fg=CYAN, bg=PANEL, font=("Consolas", 11, "bold")).pack(anchor="w")
        wrap = tk.Frame(inner, bg=BLUE, padx=1, pady=1)
        wrap.pack(fill=tk.X, pady=(8, 0))
        self._var = tk.StringVar()
        e = tk.Entry(wrap, textvariable=self._var, bg="#060d1e", fg=TEXT, insertbackground=CYAN, relief=tk.FLAT, font=("Segoe UI", 12))
        add_context_menu(e)
        e.pack(fill=tk.X, ipady=10, padx=1, pady=1)
        e.focus_set()
        e.bind("<Return>", lambda _: self._go(on_search))
        e.bind("<Escape>", lambda _: self.win.destroy())

    def _go(self, on_search):
        q = self._var.get().strip()
        if q: on_search(q)
        self.win.destroy()


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  REMINDER TOAST (РІСЃРїР»С‹РІР°СЋС‰РµРµ СѓРІРµРґРѕРјР»РµРЅРёРµ РІРЅСѓС‚СЂРё РїСЂРёР»РѕР¶РµРЅРёСЏ)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class ReminderToast:
    def __init__(self, parent, text: str):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        sw = self.win.winfo_screenwidth()
        self.win.geometry(f"360x90+{sw - 380}+20")
        self.win.configure(bg=AMBER)
        inner = tk.Frame(self.win, bg="#1a1000", padx=2, pady=2)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        tk.Label(inner, text="вЏ°  JARVIS РќРђРџРћРњРРќРђРќРР•", fg=AMBER, bg="#1a1000", font=("Consolas", 9, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(inner, text=text, fg=TEXT, bg="#1a1000", font=("Segoe UI", 11), wraplength=320).pack(anchor="w", padx=10)
        tk.Button(inner, text="вњ–", command=self.win.destroy, bg="#1a1000", fg=DIM, relief=tk.FLAT, bd=0, cursor="hand2").pack(anchor="e", padx=6)
        self.win.after(8000, self._close)

    def _close(self):
        try: self.win.destroy()
        except Exception: pass


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  MAIN APPLICATION
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
class JarvisUI:
    def __init__(self, root: tk.Tk):
        self.root        = root
        self._busy       = False
        self._q: queue.Queue = queue.Queue()
        self._anim_id    = None
        self._user_city  = CONFIG.get("default_city", "Moscow")
        self._voice_state = "idle"  # idle | listening | processing | error

        root.title("JARVIS  в—€  Neural Intelligence Core  v4.0")
        root.geometry("1480x900")
        root.minsize(1100, 720)
        root.configure(bg=BG)

        self.mode_var   = tk.StringVar(value="safe")
        self.input_var  = tk.StringVar()
        self.status_var = tk.StringVar(value="InitialisingвЂ¦")

        self.conv = get_conversation("gui") if JARVIS_OK else None

        # РњРµРЅРµРґР¶РµСЂ РЅР°РїРѕРјРёРЅР°РЅРёР№
        self._reminders = ReminderManager(on_remind=self._on_reminder)

        # Р“РѕР»РѕСЃРѕРІРѕР№ РєРѕРЅС‚СЂРѕР»Р»РµСЂ
        self._voice = VoiceController(on_text=self._on_voice_text, on_state=self._on_voice_state)

        # LocalParser СЃ РїРѕРґРґРµСЂР¶РєРѕР№ Р±СЂР°СѓР·РµСЂР° Рё РЅР°РїРѕРјРёРЅР°РЅРёР№
        self._parser = LocalParser(
            city_fn=lambda: self._user_city,
            reminder_mgr=self._reminders,
            open_browser=self._open_browser_url,
        )

        self._build()
        self._greet()
        self._tick_clock()
        self._tick_bg()
        self._poll_queue()

        threading.Thread(target=self._fetch_location, daemon=True).start()
        threading.Thread(target=self._metrics_loop,   daemon=True).start()

    # в”Ђв”Ђ BUILD в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _build(self):
        self.bg_cv = StarField(self.root)
        self.bg_cv.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#060e1d", highlightthickness=1, highlightbackground=BORDER)
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))

        logo = tk.Frame(hdr, bg="#060e1d")
        logo.pack(side=tk.LEFT, padx=22, pady=14)
        tk.Label(logo, text="в—€  JARVIS", fg=CYAN, bg="#060e1d", font=("Consolas", 30, "bold")).pack(anchor="w")
        ai_txt = "GPT READY" if GPT.available() else ("JARVIS AI" if JARVIS_OK else "STANDALONE")
        ai_clr = GREEN if GPT.available() else (CYAN if JARVIS_OK else AMBER)
        tk.Label(logo, text=f"NEURAL INTELLIGENCE CORE  В·  v4.0  В·  {ai_txt}",
                 fg=ai_clr, bg="#060e1d", font=("Consolas", 9)).pack(anchor="w", pady=(2, 0))

        mrow = tk.Frame(hdr, bg="#060e1d")
        mrow.pack(side=tk.RIGHT, padx=(0, 14), pady=12, fill=tk.Y)
        self._metrics: dict[str, tk.Label] = {}
        for name, clr in [("CPU", CYAN), ("RAM", PURPLE), ("DISK D:", GREEN), ("AI", AMBER)]:
            card = tk.Frame(mrow, bg=BG, highlightthickness=1, highlightbackground=clr, padx=14, pady=5)
            card.pack(side=tk.LEFT, padx=3)
            tk.Label(card, text=name, fg=clr, bg=BG, font=("Segoe UI", 8, "bold")).pack()
            vl = tk.Label(card, text="---", fg=TEXT, bg=BG, font=("Consolas", 15, "bold"))
            vl.pack()
            self._metrics[name] = vl

        s_btn = tk.Button(mrow, text="вљ™", command=self._open_settings, bg=BG, fg=DIM, relief=tk.FLAT, bd=0,
                          highlightthickness=1, highlightbackground=BORDER, font=("Segoe UI", 14), cursor="hand2", padx=10, pady=10)
        s_btn.pack(side=tk.LEFT, padx=(6, 0))
        s_btn.bind("<Enter>", lambda e: s_btn.configure(fg=AMBER, highlightbackground=AMBER))
        s_btn.bind("<Leave>", lambda e: s_btn.configure(fg=DIM,   highlightbackground=BORDER))

        clk = tk.Frame(hdr, bg="#060e1d")
        clk.pack(side=tk.RIGHT, padx=(0, 22), pady=12)
        self._time_lbl = tk.Label(clk, text="--:--:--", fg=CYAN, bg="#060e1d", font=("Consolas", 26, "bold"), cursor="hand2")
        self._time_lbl.pack(anchor="e")
        self._time_lbl.bind("<Button-1>", lambda _: TimePopup(self.root))
        tk.Label(clk, text="РЅР°Р¶РјРё в†’ РїРѕРїР°Рї", fg=DIM, bg="#060e1d", font=("Segoe UI", 7)).pack(anchor="e")
        self._date_lbl = tk.Label(clk, text="", fg=DIM, bg="#060e1d", font=("Segoe UI", 9))
        self._date_lbl.pack(anchor="e")

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        self._build_sidebar(body)
        self._build_main(body)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=274, highlightthickness=1, highlightbackground=BORDER)
        sb.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sb.pack_propagate(False)

        hd = tk.Frame(sb, bg=PANEL, padx=14, pady=12)
        hd.pack(fill=tk.X)
        tk.Label(hd, text="в—€  QUICK LAUNCH", fg=CYAN, bg=PANEL, font=("Consolas", 10, "bold")).pack(anchor="w")
        tk.Label(hd, text="Р’СЃРµ С„СѓРЅРєС†РёРё СЂР°Р±РѕС‚Р°СЋС‚ Р±РµР· AI", fg=DIM, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        tk.Frame(sb, bg=BORDER, height=1).pack(fill=tk.X, padx=12)

        self._sec(sb, "SYSTEM")
        self._btn(sb, "рџ“Ѓ  РџСЂРѕРІРѕРґРЅРёРє D:\\Jarvis",   GREEN,  fn=lambda: self._direct(self._open_explorer))
        self._btn(sb, "рџ•ђ  Р”Р°С‚Р° Рё Р’СЂРµРјСЏ",           CYAN,   fn=lambda: self._direct(lambda: TimePopup(self.root)))
        self._btn(sb, "рџ’»  РџСЂРѕС†РµСЃСЃС‹ СЃРёСЃС‚РµРјС‹",       BLUE,   fn=lambda: self._direct_chat(DA.show_processes, "execute"))
        self._btn(sb, "рџ“Љ  РњРµСЃС‚Рѕ РЅР° РґРёСЃРєРµ D:",      GREEN,  fn=lambda: self._direct_chat(lambda: DA.show_disk("D:"), "execute"))

        self._sec(sb, "AI & WEB")
        self._btn(sb, "рџЊ¤  РџРѕРіРѕРґР° (Р°РІС‚Рѕ-Р»РѕРєР°С†РёСЏ)",  AMBER,  fn=lambda: self._direct_chat(lambda: DA.get_weather(self._user_city), "weather"))
        self._btn(sb, "рџ”Ќ  РџРѕРёСЃРє РІ Р±СЂР°СѓР·РµСЂРµ",       CYAN,   fn=lambda: SearchPopup(self.root, self._open_browser_search))
        self._btn(sb, "рџЊђ  Р’РЅСѓС‚СЂРµРЅРЅРёР№ Р±СЂР°СѓР·РµСЂ",     PURPLE, fn=lambda: self._direct(lambda: BrowserWindow(self.root)))
        self._btn(sb, "рџ“Ќ  РўРµРєСѓС‰Р°СЏ РїР°РїРєР°",          BLUE,   fn=lambda: self._direct_chat(DA.show_dir, "execute"))

        self._sec(sb, "APPS")
        self._btn(sb, "рџ“ќ  Р‘Р»РѕРєРЅРѕС‚",               PINK,   fn=lambda: self._direct(lambda: subprocess.Popen(["notepad"])))
        self._btn(sb, "рџ–©  РљР°Р»СЊРєСѓР»СЏС‚РѕСЂ",            BLUE,   fn=lambda: self._direct(lambda: subprocess.Popen(["calc"])))

        self._sec(sb, "РќРђРџРћРњРРќРђРќРРЇ")
        self._btn(sb, "вЏ°  Р”РѕР±Р°РІРёС‚СЊ РЅР°РїРѕРјРёРЅР°РЅРёРµ",   AMBER,  fn=self._reminder_dialog)
        self._btn(sb, "рџ“‹  РњРѕРё РЅР°РїРѕРјРёРЅР°РЅРёСЏ",        DIM,    fn=lambda: self._direct_chat(self._reminders.list_reminders, "reminder"))

        tk.Frame(sb, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=10)

        mf = tk.Frame(sb, bg=PANEL, padx=14)
        mf.pack(fill=tk.X)
        tk.Label(mf, text="в—€  Р Р•Р–РРњ", fg=AMBER, bg=PANEL, font=("Consolas", 9, "bold")).pack(anchor="w", pady=(0, 6))
        for val, txt, clr in [("safe", "рџ”’  Safe Preview", GREEN), ("real", "вљЎ  Real Execute", AMBER)]:
            rb = tk.Radiobutton(mf, text=txt, variable=self.mode_var, value=val, fg=DIM, bg=PANEL, selectcolor="#0c1830",
                                activebackground=PANEL, activeforeground=clr, font=("Segoe UI", 9), bd=0, relief=tk.FLAT,
                                indicatoron=False, padx=12, pady=8, cursor="hand2")
            rb.pack(fill=tk.X, pady=2)
            rb.bind("<Enter>", lambda e, b=rb, c=clr: b.configure(fg=c, bg="#0c1830"))
            rb.bind("<Leave>", lambda e, b=rb: b.configure(fg=DIM, bg=PANEL))

        tk.Frame(sb, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=10)
        tk.Label(sb, text="в—€  NODE STATE", fg=PURPLE, bg=PANEL, font=("Consolas", 9, "bold"), padx=14).pack(anchor="w", pady=(0, 4))
        self._node = tk.Text(sb, bg="#030c18", fg="#3a6090", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 8),
                             height=7, padx=10, pady=8, highlightthickness=0)
        self._node.pack(fill=tk.X, padx=8, pady=(0, 8))
        self._node_set(
            f"PROJECT  : D:\\Jarvis\n"
            f"VERSION  : Ultra v4.0\n"
            f"GPT      : {'ready' if GPT.available() else 'no key'}\n"
            f"BROWSER  : {'tkinterweb' if TKWEB_OK else 'missing'}\n"
            f"VOICE    : {'ready' if SR_OK else 'no module'}\n"
            f"REMIND   : active\n"
            f"LOCATION : fetchingвЂ¦\n"
        )

    def _sec(self, parent, title: str):
        f = tk.Frame(parent, bg=PANEL, padx=14)
        f.pack(fill=tk.X, pady=(8, 2))
        tk.Label(f, text=title, fg=DIM, bg=PANEL, font=("Segoe UI", 7, "bold")).pack(anchor="w")

    def _btn(self, parent, label: str, accent: str, fn=None):
        btn = tk.Button(parent, text=label, command=fn or (lambda: None), bg="#0a1628", fg=DIM,
                        activebackground=THM["hover"], activeforeground=BRIGHT, relief=tk.FLAT, bd=0,
                        anchor="w", padx=14, pady=9, font=("Segoe UI", 9), cursor="hand2",
                        highlightthickness=1, highlightbackground=THM["brd"])
        btn.pack(fill=tk.X, padx=8, pady=2)
        btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=CYAN, bg=THM["brd"], highlightbackground=CYAN))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=DIM, bg="#0a1628", highlightbackground=THM["brd"]))

    def _build_main(self, parent):
        main = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        top = tk.Frame(main, bg=PANEL, padx=16, pady=10)
        top.grid(row=0, column=0, sticky="ew")
        tk.Label(top, text="COMMAND DECK", fg=TEXT, bg=PANEL, font=("Consolas", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(top, text="  В·  Neural conversation interface", fg=DIM, bg=PANEL, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        clr_btn = tk.Button(top, text="вњ–  CLEAR", command=self._clear, bg="#200818", fg=DIM, relief=tk.FLAT, bd=0,
                            font=("Segoe UI", 9), cursor="hand2", padx=10, pady=4)
        clr_btn.pack(side=tk.RIGHT)
        clr_btn.bind("<Enter>", lambda e: clr_btn.configure(fg=RED, bg="#3a0828"))
        clr_btn.bind("<Leave>", lambda e: clr_btn.configure(fg=DIM, bg="#200818"))
        tk.Frame(main, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew")

        self.chat = ChatArea(main)
        self.chat.grid(row=1, column=0, sticky="nsew", padx=10, pady=(8, 4))

        tw = tk.Frame(main, bg="#050b18", highlightthickness=1, highlightbackground="#0a1e3a")
        tw.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))
        tk.Label(tw, text="в–ѕ  THINKING CONSOLE", fg=PURPLE, bg="#050b18", font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=10, pady=(5, 3))
        tk.Label(tw, text="Cognitive trace", fg=DIM, bg="#050b18", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        self._think_log = tk.Text(tw, bg="#030810", fg="#3a6090", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 8),
                                  height=3, padx=10, pady=6, highlightthickness=0)
        self._think_log.pack(fill=tk.X)

        inp = tk.Frame(main, bg=PANEL, padx=14, pady=10)
        inp.grid(row=3, column=0, sticky="ew")
        tk.Label(inp, textvariable=self.status_var, fg=CYAN, bg=PANEL, font=("Segoe UI", 9), anchor="w").pack(fill=tk.X, pady=(0, 6))

        irow = tk.Frame(inp, bg=PANEL)
        irow.pack(fill=tk.X)
        irow.grid_columnconfigure(0, weight=1)

        ew = tk.Frame(irow, bg=BLUE, padx=1, pady=1)
        ew.grid(row=0, column=0, sticky="ew")
        self._entry = tk.Entry(ew, textvariable=self.input_var, bg="#060d1e", fg=TEXT,
                               insertbackground=CYAN, relief=tk.FLAT, font=("Segoe UI", 12), highlightthickness=0)
        add_context_menu(self._entry)
        self._entry.pack(fill=tk.X, ipady=13, padx=1, pady=1)
        self._entry.bind("<Return>", lambda _: self._submit())
        self._entry.focus_set()

        # РљРЅРѕРїРєР° РјРёРєСЂРѕС„РѕРЅР°
        self._mic_btn = tk.Button(irow, text="рџЋ¤", command=self._toggle_voice, bg="#0c2040", fg=DIM,
                                   activebackground="#1a4080", relief=tk.FLAT, bd=0,
                                   font=("Segoe UI", 14), cursor="hand2", padx=14, pady=12,
                                   highlightthickness=1, highlightbackground=BORDER)
        self._mic_btn.grid(row=0, column=1, padx=(6, 0))
        self._mic_btn.bind("<Enter>", lambda e: self._mic_btn.configure(fg=GREEN, highlightbackground=GREEN))
        self._mic_btn.bind("<Leave>", lambda e: self._update_mic_btn())

        send = tk.Button(irow, text="в–¶  SEND", command=self._submit, bg="#1040a0", fg=BRIGHT,
                         activebackground="#2860d0", relief=tk.FLAT, bd=0, padx=22, pady=13,
                         font=("Segoe UI", 10, "bold"), cursor="hand2")
        send.grid(row=0, column=2, padx=(6, 0))
        send.bind("<Enter>", lambda e: send.configure(bg="#2860d0"))
        send.bind("<Leave>", lambda e: send.configure(bg="#1040a0"))

        pr = tk.Frame(inp, bg=PANEL)
        pr.pack(fill=tk.X, pady=(8, 0))
        self._pills: dict[str, tk.Label] = {}
        for name, val, clr in [
            ("MODE",     "SAFE",   GREEN),
            ("AI",       "GPT" if GPT.available() else "STANDALONE", GREEN if GPT.available() else AMBER),
            ("LOCATION", "...",   DIM),
            ("VOICE",    "OFF" if not SR_OK else "READY", DIM if not SR_OK else GREEN),
            ("REMIND",   "0",     DIM),
        ]:
            pf = tk.Frame(pr, bg=PANEL2, highlightthickness=1, highlightbackground=BORDER)
            pf.pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(pf, text=name, fg=DIM, bg=PANEL2, font=("Segoe UI", 7, "bold")).pack(padx=10, pady=(3, 0))
            vl = tk.Label(pf, text=val, fg=clr, bg=PANEL2, font=("Consolas", 9, "bold"))
            vl.pack(padx=10, pady=(0, 3))
            self._pills[name] = vl

    # в”Ђв”Ђ VOICE в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _toggle_voice(self):
        if not SR_OK:
            messagebox.showinfo("Р“РѕР»РѕСЃРѕРІРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ",
                                "РЈСЃС‚Р°РЅРѕРІРё SpeechRecognition:\n\npython -m pip install SpeechRecognition pyaudio")
            return
        if self._voice_state == "idle":
            self._voice.listen_once()
        
    def _on_voice_text(self, text: str):
        self.root.after(0, lambda: self._submit(forced=text))

    def _on_voice_state(self, state: str):
        self._voice_state = state
        colors = {"idle": DIM, "listening": GREEN, "processing": AMBER, "error": RED}
        icons  = {"idle": "рџЋ¤", "listening": "рџ”ґ", "processing": "вЏі", "error": "вќЊ"}
        labels = {"idle": "READY" if SR_OK else "OFF", "listening": "LISTENING", "processing": "...", "error": "ERR"}
        self.root.after(0, lambda: (
            self._mic_btn.configure(fg=colors.get(state, DIM)),
            self._pill("VOICE", labels.get(state, state), colors.get(state, DIM)),
            self._update_mic_btn()
        ))

    def _update_mic_btn(self):
        colors = {"idle": DIM, "listening": GREEN, "processing": AMBER, "error": RED}
        c = colors.get(self._voice_state, DIM)
        self._mic_btn.configure(fg=c, highlightbackground=c if self._voice_state != "idle" else BORDER)

    # в”Ђв”Ђ BROWSER в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _open_browser_url(self, url: str):
        BrowserWindow(self.root, url)

    def _open_browser_search(self, query: str):
        url = "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(query)
        self._open_browser_url(url)
        self._direct_chat(lambda: f"рџ”Ќ  РС‰Сѓ РІРѕ РІРЅСѓС‚СЂРµРЅРЅРµРј Р±СЂР°СѓР·РµСЂРµ:\nВ«{query}В»", "search")

    # в”Ђв”Ђ REMINDERS в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _on_reminder(self, text: str):
        """Р’С‹Р·С‹РІР°РµС‚СЃСЏ РєРѕРіРґР° СЃСЂР°Р±Р°С‚С‹РІР°РµС‚ РЅР°РїРѕРјРёРЅР°РЅРёРµ."""
        self.root.after(0, lambda: (
            ReminderToast(self.root, text),
            self.chat.add_jarvis(f"вЏ°  РќР°РїРѕРјРёРЅР°РЅРёРµ: {text}", intent="reminder"),
            self._pill("REMIND", "!", AMBER)
        ))

    def _reminder_dialog(self):
        """Р”РёР°Р»РѕРі РґРѕР±Р°РІР»РµРЅРёСЏ РЅР°РїРѕРјРёРЅР°РЅРёСЏ."""
        win = tk.Toplevel(self.root)
        win.title("в—€  Р”РѕР±Р°РІРёС‚СЊ РЅР°РїРѕРјРёРЅР°РЅРёРµ")
        win.geometry("440x200+250+200")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        outer = tk.Frame(win, bg=AMBER, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        tk.Label(inner, text="вЏ°  РќРђРџРћРњРРќРђРќРР•", fg=AMBER, bg=PANEL, font=("Consolas", 11, "bold")).pack(anchor="w")
        tk.Label(inner, text="РўРµРєСЃС‚ РЅР°РїРѕРјРёРЅР°РЅРёСЏ:", fg=DIM, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 2))
        wrap1 = tk.Frame(inner, bg=AMBER, padx=1, pady=1)
        wrap1.pack(fill=tk.X)
        txt_var = tk.StringVar()
        e1 = tk.Entry(wrap1, textvariable=txt_var, bg="#060d1e", fg=TEXT, insertbackground=AMBER, relief=tk.FLAT, font=("Segoe UI", 11))
        add_context_menu(e1)
        e1.pack(fill=tk.X, ipady=8, padx=1, pady=1)

        tk.Label(inner, text="РљРѕРіРґР°? (РЅР°РїСЂ: С‡РµСЂРµР· 10 РјРёРЅСѓС‚, С‡РµСЂРµР· 1 С‡Р°СЃ):", fg=DIM, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 2))
        wrap2 = tk.Frame(inner, bg=AMBER, padx=1, pady=1)
        wrap2.pack(fill=tk.X)
        when_var = tk.StringVar(value="С‡РµСЂРµР· 5 РјРёРЅСѓС‚")
        e2 = tk.Entry(wrap2, textvariable=when_var, bg="#060d1e", fg=TEXT, insertbackground=AMBER, relief=tk.FLAT, font=("Segoe UI", 11))
        add_context_menu(e2)
        e2.pack(fill=tk.X, ipady=8, padx=1, pady=1)

        def _set():
            full = f"РЅР°РїРѕРјРЅРё {when_var.get()} {txt_var.get()}"
            result = self._reminders.parse_and_add(full)
            self.chat.add_jarvis(result, intent="reminder")
            self._pill("REMIND", str(len(self._reminders._reminders)), AMBER)
            win.destroy()

        tk.Button(inner, text="вњ”  РЈСЃС‚Р°РЅРѕРІРёС‚СЊ", command=_set, bg="#403000", fg=AMBER, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 10, "bold"), cursor="hand2", padx=16, pady=8).pack(pady=(12, 0))

    # в”Ђв”Ђ SETTINGS в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _open_settings(self):
        SettingsWindow(self.root, CONFIG, on_save=self._on_settings_saved)

    def _on_settings_saved(self, new_cfg: dict):
        CONFIG.update(new_cfg)
        if new_cfg.get("default_city"): self._user_city = new_cfg["default_city"]
        gpt_ok = GPT.available()
        self._pill("AI", "GPT" if gpt_ok else "STANDALONE", GREEN if gpt_ok else AMBER)

    # в”Ђв”Ђ CHAT LOGIC в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    def _greet(self):
        self.chat.add_system("Session started  В·  " + datetime.now().strftime("%d %b %Y  %H:%M"))
        gpt_note = "рџ¤–  GPT РіРѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ." if GPT.available() else "вљ™пёЏ  Р”Р»СЏ AI вЂ” РІРІРµРґРё OpenAI РєР»СЋС‡ РІ РЅР°СЃС‚СЂРѕР№РєР°С…."
        voice_note = "рџЋ¤  Р“РѕР»РѕСЃРѕРІРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ Р°РєС‚РёРІРЅРѕ." if SR_OK else ""
        self.chat.add_jarvis(
            f"JARVIS v4.0 online.\n\n{gpt_note}\n{voice_note}\n\n"
            "Р’СЃРµ РєРЅРѕРїРєРё СЃР°Р№РґР±Р°СЂР° СЂР°Р±РѕС‚Р°СЋС‚ Р±РµР· AI.\n"
            "рџ”Ќ РџРѕРёСЃРє С‚РµРїРµСЂСЊ РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ РІРѕ РІРЅСѓС‚СЂРµРЅРЅРµРј Р±СЂР°СѓР·РµСЂРµ.",
            intent="chat",
        )
        self.status_var.set("All systems nominal  В·  v4.0 active")

    def _think(self, msg: str):
        self._think_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]  {msg}\n")
        self._think_log.see(tk.END)

    def _pill(self, name: str, val: str, clr: str):
        if name in self._pills: self._pills[name].config(text=val, fg=clr)

    def _node_set(self, text: str):
        self._node.config(state=tk.NORMAL)
        self._node.delete("1.0", tk.END)
        self._node.insert("1.0", text.rstrip("\n"))
        self._node.config(state=tk.DISABLED)

    def _clear(self):
        for w in self.chat._inner.winfo_children(): w.destroy()
        self._think_log.delete("1.0", tk.END)
        self.chat.add_system("Log cleared  В·  " + datetime.now().strftime("%H:%M"))
        self.chat.add_jarvis("Cleared. Ready, Commander.", intent="chat")
        self.status_var.set("Log cleared.")
        GPT.reset()

    def _submit(self, forced: str = None):
        if self._busy: return
        text = forced if forced else self.input_var.get().strip()
        if not text: return
        self.input_var.set("")
        self.chat.add_user(text)
        refs = self.chat.add_jarvis("", intent="chat")
        self._busy = True
        self._start_anim(refs["tv"])
        self._think(f"INPUT    в–ё  {text}")
        self.status_var.set("рџ§   ProcessingвЂ¦")
        self._pill("AI", "BUSY", AMBER)
        threading.Thread(target=self._bg_process, args=(text, refs), daemon=True).start()

    def _start_anim(self, tv: tk.StringVar):
        frames = ["в–ЊВ·   ", "в–ЊВ·В·  ", "в–ЊВ·В·В· ", "в–ЊВ·В·В·В·"]
        def _anim(n: int = 0):
            if not self._busy: return
            tv.set(frames[n % 4])
            self._anim_id = self.root.after(260, _anim, n + 1)
        self._anim_id = self.root.after(80, _anim)

    def _stop_anim(self):
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None

    def _bg_process(self, text: str, refs: dict):
        self._q.put((refs, self._process(text)))

    def _process(self, text: str) -> dict:
        # 1. Р›РѕРєР°Р»СЊРЅС‹Р№ РїР°СЂСЃРµСЂ
        local = self._parser.parse(text, self.root)
        if local is not None:
            self._think(f"LOCAL    в–ё  intent={local['intent']}")
            return local

        # 2. GPT (OpenAI)
        if GPT.available():
            self._think("AI       в–ё  GPT request")
            answer = GPT.ask(text)
            if answer:
                return {"text": answer, "intent": "chat"}

        # 3. Jarvis AI РјРѕРґСѓР»СЊ
        if JARVIS_OK:
            try:
                history = self.conv.get_messages() if self.conv else []
                plan    = plan_command(text, conversation_history=history)
                self._think(f"JARVIS   в–ё  intent={plan.intent}")
                if getattr(plan, "source", "") == "fallback":
                    return {"text": "вљ™пёЏ  AI РІ fallback-СЂРµР¶РёРјРµ. Р”РѕР±Р°РІСЊ API-РєР»СЋС‡ РІ вљ™ РќР°СЃС‚СЂРѕР№РєРё.", "intent": "answer"}
                if plan.intent == "chat":
                    return {"text": plan.reason, "intent": "chat"}
                if not plan.command or plan.intent == "answer":
                    return {"text": plan.reason, "intent": "answer"}
                dec = check_command(plan.command)
                if not dec.allowed:
                    return {"text": f"в›”  Р—Р°Р±Р»РѕРєРёСЂРѕРІР°РЅРѕ: {dec.reason}", "intent": "execute"}
                if self.mode_var.get() == "safe":
                    return {"text": f"рџ”Ќ  Safe Preview\n\n{plan.reason}\n\n`{plan.command}`\n\nРџРµСЂРµРєР»СЋС‡Рё СЂРµР¶РёРј РЅР° Real Execute.", "intent": "execute"}
                if JARVIS_OK: snd.play('execute')
                res = run_command(plan.command)
                return {"text": f"{plan.reason}\n\n`{plan.command}`  в†’  exit {res.exit_code}", "intent": "execute"}
            except Exception as exc:
                self._think(f"JARVIS ERR в–ё  {exc}")

        # 4. Fallback
        return {
            "text": "в„№пёЏ  Р”Р»СЏ AI-РѕС‚РІРµС‚РѕРІ РІРІРµРґРё API РљР»СЋС‡ РёР»Рё Base URL РІ вљ™ РќР°СЃС‚СЂРѕР№РєРё в†’ AI & Web.\n\n"
                    "Р”РѕСЃС‚СѓРїРЅС‹Рµ РєРѕРјР°РЅРґС‹ Р±РµР· AI:\n"
                    "вЂў РїРѕРєР°Р¶Рё РїСЂРѕС†РµСЃСЃС‹ / РґРёСЃРє / С„Р°Р№Р»С‹\nвЂў РїРѕРіРѕРґР° / РІСЂРµРјСЏ / РґР°С‚Р°\n"
                    "вЂў РЅР°Р№РґРё [Р·Р°РїСЂРѕСЃ]\nвЂў РЅР°РїРѕРјРЅРё С‡РµСЂРµР· 5 РјРёРЅСѓС‚ [С‚РµРєСЃС‚]",
            "intent": "answer"
        }

    def _poll_queue(self):
        try:
            while True:
                refs, result = self._q.get_nowait()
                self._stop_anim()
                text, intent = result["text"], result.get("intent", "chat")
                self.chat.update_bubble(refs, text, intent)
                self.status_var.set(f"вњ“  Done  В·  {intent}")
                self._pill("AI", "GPT" if GPT.available() else "READY", GREEN if GPT.available() else CYAN)
                self._think(f"DONE     в–ё  intent={intent}")
                self._busy = False
        except queue.Empty: pass
        self.root.after(60, self._poll_queue)

    def _direct(self, fn):
        try: fn()
        except Exception as exc: messagebox.showerror("Error", str(exc))

    def _direct_chat(self, fn, intent: str = "execute"):
        if self._busy: return
        refs = self.chat.add_jarvis("вЏі  Р’С‹РїРѕР»РЅСЏСЋвЂ¦", intent=intent)
        self._think(f"DIRECT   в–ё  {intent}")
        def _run():
            try:
                text = fn() if callable(fn) else fn
                intent_r = intent
            except Exception as exc:
                text, intent_r = f"вќЊ  {exc}", "error"
            self._q.put((refs, {"text": text, "intent": intent_r}))
        threading.Thread(target=_run, daemon=True).start()

    def _open_explorer(self, path: str = "D:\\Jarvis"):
        subprocess.Popen(["explorer", path])
        self.chat.add_system(f"Explorer в†’ {path}")

    def _fetch_location(self):
        try:
            with urllib.request.urlopen("http://ip-api.com/json/?fields=city,country", timeout=6) as r:
                city = json.loads(r.read().decode("utf-8")).get("city", "Moscow")
                self._user_city = city
                self.root.after(0, self._on_location, city)
        except Exception:
            self.root.after(0, self._on_location, None)

    def _on_location(self, city):
        if city:
            self._pill("LOCATION", city[:12], GREEN)
            self.status_var.set(f"All systems nominal  В·  Location: {city}")
            current = self._node.get("1.0", tk.END)
            self._node_set(current.replace("LOCATION : fetchingвЂ¦", f"LOCATION : {city}"))
        else:
            self._pill("LOCATION", "n/a", DIM)

    def _metrics_loop(self):
        if PSUTIL_OK: psutil.cpu_percent(interval=None); time.sleep(1)
        while True:
            m = {}
            try:
                if PSUTIL_OK:
                    m["CPU"] = f"{psutil.cpu_percent(interval=None):.0f}%"
                    m["RAM"] = f"{psutil.virtual_memory().percent:.0f}%"
                    try: m["DISK D:"] = f"{psutil.disk_usage('D:\\').percent:.0f}%"
                    except: m["DISK D:"] = "n/a"
            except Exception: pass
            m["AI"] = "BUSY" if self._busy else "OK"
            self.root.after(0, self._apply_metrics, m)
            time.sleep(3)

    def _apply_metrics(self, m: dict):
        for name, val in m.items():
            if name in self._metrics: self._metrics[name].config(text=val)

    def _tick_clock(self):
        now = datetime.now()
        self._time_lbl.config(text=now.strftime("%H:%M:%S"))
        self._date_lbl.config(text=now.strftime("%A, %d %B %Y"))
        self._pill("MODE", self.mode_var.get().upper(), GREEN if self.mode_var.get() == "safe" else AMBER)
        self.root.after(1000, self._tick_clock)

    def _tick_bg(self):
        self.bg_cv.tick()
        self.root.after(40, self._tick_bg)


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
#  ENTRY POINT
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
def main():
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: (_stop_local_model(), root.destroy()))
    JarvisUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
