import subprocess
from dataclasses import dataclass
from jarvis_cmd.memory import save_fact, delete_fact
from jarvis_cmd.scheduler import add_schedule
from jarvis_cmd.system_control import SystemController
from jarvis_cmd.app_indexer import AppIndexer

@dataclass
class ExecResult:
    exit_code: int
    stdout: str
    stderr: str

indexer = AppIndexer()
sys_ctrl = SystemController()

def run_action(intent: str, command: str) -> ExecResult:
    if intent == "memory_save":
        res = save_fact(command)
        return ExecResult(0, res, "")
        
    elif intent == "memory_delete":
        res = delete_fact(command)
        return ExecResult(0, res, "")
        
    elif intent == "schedule":
        parts = command.split("|", 1)
        if len(parts) == 2:
            res = add_schedule(parts[0], parts[1])
            return ExecResult(0, res, "")
        return ExecResult(1, "", "Invalid schedule format")
        
    elif intent == "system":
        if command == "volume_up": sys_ctrl.volume_up()
        elif command == "volume_down": sys_ctrl.volume_down()
        elif command == "mute": sys_ctrl.mute_unmute()
        elif command == "play_pause": sys_ctrl.media_play_pause()
        elif command == "next": sys_ctrl.media_next()
        elif command == "prev": sys_ctrl.media_prev()
        return ExecResult(0, f"System command executed: {command}", "")
        
    elif intent == "open_app":
        app_path = indexer.find_app(command)
        if app_path:
            try:
                subprocess.Popen(app_path, shell=True)
                return ExecResult(0, f"Opened {app_path}", "")
            except Exception as e:
                return ExecResult(1, "", str(e))
        return ExecResult(1, "", f"App not found: {command}")

    elif intent == "execute":
        # Fallback to standard shell
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return ExecResult(
            exit_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )
        
    return ExecResult(0, "No action required", "")

def run_command(command: str) -> ExecResult:
    return run_action("execute", command)