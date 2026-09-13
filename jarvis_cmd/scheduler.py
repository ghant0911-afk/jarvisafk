import time
import threading
from datetime import datetime
import json
from pathlib import Path
import re

TASKS_PATH = Path(__file__).parent.parent / "data" / "schedule.json"

def get_tasks():
    if not TASKS_PATH.exists():
        return []
    try:
        return json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    except:
        return []

def save_tasks(tasks):
    TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASKS_PATH.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")

def add_schedule(time_str: str, message: str) -> str:
    """Добавляет задачу. time_str в формате HH:MM"""
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        return "Ошибка: время должно быть в формате ЧЧ:ММ"
    
    tasks = get_tasks()
    tasks.append({"time": time_str, "message": message, "done_today": False, "last_date": ""})
    save_tasks(tasks)
    return f"Запланировано на {time_str}: {message}"

def remove_schedule(index: int) -> str:
    tasks = get_tasks()
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        save_tasks(tasks)
        return f"Удалено расписание: {removed['message']}"
    return "Неверный индекс расписания"

def _scheduler_loop(callback):
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today_date = now.strftime("%Y-%m-%d")
        
        tasks = get_tasks()
        changed = False
        
        for task in tasks:
            # Сброс флага на следующий день
            if task.get("last_date") != today_date:
                task["done_today"] = False
                task["last_date"] = today_date
                changed = True
                
            if current_time == task["time"] and not task["done_today"]:
                task["done_today"] = True
                changed = True
                # Вызываем коллбек (например, проговорить или выполнить команду)
                callback(task["message"])
                
        if changed:
            save_tasks(tasks)
            
        time.sleep(10)

def start_scheduler(callback):
    t = threading.Thread(target=_scheduler_loop, args=(callback,), daemon=True)
    t.start()