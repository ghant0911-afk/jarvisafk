import os
import sys
from pathlib import Path
import importlib.util

SKILLS_DIR = Path(__file__).parent / "skills"

def ensure_skills_dir():
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    init_file = SKILLS_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

def create_skill(name: str, code: str) -> str:
    """Сохраняет новый Python навык (Hermes concept)"""
    ensure_skills_dir()
    safe_name = name.replace(" ", "_").replace("-", "_").lower()
    if not safe_name.endswith(".py"):
        safe_name += ".py"
        
    skill_path = SKILLS_DIR / safe_name
    skill_path.write_text(code, encoding="utf-8")
    return f"Навык {safe_name} успешно создан и загружен."

def execute_skill(name: str, *args, **kwargs) -> str:
    """Выполняет навык"""
    safe_name = name.replace(" ", "_").replace("-", "_").lower()
    if not safe_name.endswith(".py"):
        safe_name += ".py"
        
    skill_path = SKILLS_DIR / safe_name
    if not skill_path.exists():
        return f"Навык {safe_name} не найден."
        
    try:
        spec = importlib.util.spec_from_file_location(safe_name[:-3], str(skill_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'run'):
            return str(module.run(*args, **kwargs))
        return "В навыке нет функции run()"
    except Exception as e:
        return f"Ошибка выполнения навыка: {e}"

def list_skills():
    ensure_skills_dir()
    return [f.name for f in SKILLS_DIR.glob("*.py") if f.name != "__init__.py"]