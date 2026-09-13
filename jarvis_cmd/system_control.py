import os
import sys
import subprocess
import time
from datetime import datetime

class SystemController:
    """Модуль прямого управления Windows без багов"""

    def __init__(self, data_dir=None):
        from jarvis_cmd.app_indexer import AppIndexer
        from jarvis_cmd.screen_automator import ScreenAutomator
        self.indexer = AppIndexer(data_dir=data_dir)
        self.screen = ScreenAutomator()
        # При старте, если каталог пустой, выполняем быстрое сканирование
        if not self.indexer.catalog:
            self.indexer.rescan_all()

    def get_system_status(self):
        """Возвращает сводку по загрузке CPU, памяти и дисков"""
        info = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "ram_percent": 0.0,
            "disk_free_gb": 0.0
        }

        try:
            import psutil
            info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            info["ram_total_gb"] = round(ram.total / (1024 ** 3), 1)
            info["ram_used_gb"] = round(ram.used / (1024 ** 3), 1)
            info["ram_percent"] = ram.percent

            disk = psutil.disk_usage("C:\\")
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 1)
        except Exception:
            # Native PowerShell fallback
            ps_cmd = 'Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json'
            res = subprocess.run(["powershell", "-c", ps_cmd], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout:
                import json
                try:
                    data = json.loads(res.stdout)
                    total = data.get("TotalVisibleMemorySize", 0) / 1024 / 1024
                    free = data.get("FreePhysicalMemory", 0) / 1024 / 1024
                    info["ram_total_gb"] = round(total, 1)
                    info["ram_used_gb"] = round(total - free, 1)
                    if total > 0:
                        info["ram_percent"] = round(((total - free) / total) * 100, 1)
                except Exception:
                    pass

        return info

    def take_screenshot(self, output_path=None):
        """Делает снимок экрана и сохраняет по указанному пути"""
        if output_path is None:
            output_path = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"jarvis_screen_{int(time.time())}.png")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            import threading
            import ctypes
            grab_result = {}

            def _grab_worker():
                try:
                    user32 = ctypes.windll.user32
                    hwinsta = user32.OpenWindowStationW('WinSta0', False, 0x037F)
                    if hwinsta:
                        user32.SetProcessWindowStation(hwinsta)
                    hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
                    if hdesk:
                        user32.SetThreadDesktop(hdesk)
                    from PIL import ImageGrab
                    im = ImageGrab.grab()
                    im.save(output_path, "PNG")
                    grab_result["ok"] = True
                except Exception as e:
                    grab_result["err"] = str(e)

            t = threading.Thread(target=_grab_worker)
            t.start()
            t.join(timeout=3.0)
            if grab_result.get("ok") and os.path.exists(output_path):
                return output_path
        except Exception:
            # Native PowerShell fallback for screenshot
            ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
$Bitmap = New-Object System.Drawing.Bitmap $Screen.Width, $Screen.Height
$Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
$Graphics.CopyFromScreen($Screen.Left, $Screen.Top, 0, 0, $Bitmap.Size)
$Bitmap.Save("{output_path}", [System.Drawing.Imaging.ImageFormat]::Png)
$Graphics.Dispose()
$Bitmap.Dispose()
'''
            res = subprocess.run(["powershell", "-c", ps_script], capture_output=True)
            if os.path.exists(output_path):
                return output_path
            return None

    def open_app(self, name_or_key):
        """
        Умное открытие приложения, игры Steam, ярлыка или системного инструмента.
        Возвращает (успех: bool, каноническое_имя: str)
        """
        key = name_or_key.lower().strip()

        # Специальные интернет-ресурсы
        web_map = {
            "ютуб": "https://youtube.com",
            "youtube": "https://youtube.com",
            "гугл": "https://google.com",
            "яндекс": "https://ya.ru",
            "почта": "https://mail.google.com",
            "музыка онлайн": "https://music.yandex.ru"
        }
        if key in web_map:
            import webbrowser
            webbrowser.open(web_map[key])
            return True, key.capitalize()

        # 1. Сначала пробуем через интеллектуальный AppIndexer (Steam, Ярлыки, Память)
        success, app_name, msg = self.indexer.launch(key)
        if success:
            return True, app_name

        # 2. Системные резервные пути Windows
        app_map = {
            "проводник": ("explorer.exe", "shell:MyComputerFolder"),
            "explorer": ("explorer.exe", "shell:MyComputerFolder"),
            "файлы": ("explorer.exe", "shell:MyComputerFolder"),
            "загрузки": ("explorer.exe", "shell:Downloads"),
            "документы": ("explorer.exe", "shell:Personal"),
            "диспетчер задач": ("taskmgr.exe", ""),
            "taskmgr": ("taskmgr.exe", ""),
            "калькулятор": ("calc.exe", ""),
            "блокнот": ("notepad.exe", ""),
            "браузер": ("https://www.google.com", ""),
            "стим": ("steam://", ""),
            "steam": ("steam://", ""),
            "обсидиан": ("obsidian://", "")
        }

        if key in app_map:
            target_entry = app_map[key]
            try:
                import ctypes
                if isinstance(target_entry, tuple):
                    exe_name, args = target_entry
                else:
                    exe_name, args = target_entry, ""

                if exe_name.startswith("http"):
                    import webbrowser
                    webbrowser.open(exe_name)
                else:
                    ret = ctypes.windll.shell32.ShellExecuteW(None, 'open', exe_name, args, None, 1)
                    if ret <= 32:
                        os.startfile(exe_name)
                return True, key.capitalize()
            except Exception as e:
                print(f"[SystemController] Ошибка запуска fallback {key}: {e}")

        # 3. Если ничего не найдено - пробуем запустить через Windows Shell
        try:
            import ctypes
            ret = ctypes.windll.shell32.ShellExecuteW(None, 'open', name_or_key, '', None, 1)
            if ret > 32:
                return True, name_or_key
            os.startfile(name_or_key)
            return True, name_or_key
        except Exception:
            return False, name_or_key

    def close_app(self, name_or_key):
        """Закрывает приложение через AppIndexer / psutil"""
        return self.indexer.close(name_or_key)

    def remember_app(self, alias, target, canonical_name=None):
        """Обучение Джарвиса новой программе или пути"""
        return self.indexer.learn(alias, target, canonical_name)

    def search_web(self, query):
        """Поиск в интернете в браузере по умолчанию"""
        import webbrowser
        import urllib.parse
        clean_q = urllib.parse.quote(query.strip())
        url = f"https://www.google.com/search?q={clean_q}"
        webbrowser.open(url)
        return True

    def rescan_apps(self):
        """Пересканирование всех установленных программ и игр"""
        return self.indexer.rescan_all()

    def change_volume(self, action="up", steps=5):
        """Регулировка громкости: up (+10%), down (-10%), mute (полностью невидимо без окон cmd/powershell)"""
        key_code = {
            "up": 0xAF,    # VK_VOLUME_UP
            "down": 0xAE,  # VK_VOLUME_DOWN
            "mute": 0xAD   # VK_VOLUME_MUTE
        }.get(action, 0xAF)

        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwinsta = user32.OpenWindowStationW('WinSta0', False, 0x037F)
            if hwinsta:
                user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)

            n_steps = 1 if action == "mute" else steps
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            for _ in range(n_steps):
                user32.keybd_event(key_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
                user32.keybd_event(key_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
                time.sleep(0.02)
            return True
        except Exception:
            return False

    def media_control(self, action="play_pause"):
        """Управление медиа: play_pause, next, prev (полностью невидимо без окон)"""
        key_code = {
            "play_pause": 0xB3,
            "next": 0xB0,
            "prev": 0xB1
        }.get(action, 0xB3)

        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwinsta = user32.OpenWindowStationW('WinSta0', False, 0x037F)
            if hwinsta:
                user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)

            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            user32.keybd_event(key_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
            user32.keybd_event(key_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return True
        except Exception:
            return False
            return True
        except Exception:
            return False

    def lock_pc(self):
        """Блокировка экрана (невидимо)"""
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception:
            return False

    def sleep_pc(self):
        """Спящий режим (невидимо)"""
        try:
            import ctypes
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return True
        except Exception:
            return False

    def shutdown_pc(self, delay_seconds=60):
        """Выключение компьютера с таймером (скрытый вызов)"""
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            f"shutdown /s /t {delay_seconds}",
            shell=True,
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True

    def cancel_shutdown(self):
        """Отмена выключения (скрытый вызов)"""
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            "shutdown /a",
            shell=True,
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True

    def restart_pc(self, delay_seconds=30):
        """Перезагрузка компьютера (скрытый вызов)"""
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            f"shutdown /r /t {delay_seconds}",
            shell=True,
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True

    # --- МЕТОДЫ ЭКРАННОЙ АВТОМАТИЗАЦИИ ---

    def type_text(self, text, press_enter=False):
        """Ввод текста в текущее поле"""
        return self.screen.type_text(text, press_enter=press_enter)

    def click_element(self, name):
        """Поиск и клик по элементу на экране"""
        return self.screen.find_and_click_element(name)

    def click_mouse(self, action="click"):
        """Клики мыши: click, double, right"""
        if action == "double":
            return self.screen.double_click_current()
        elif action == "right":
            return self.screen.right_click_current()
        return self.screen.click_current()

    def press_key(self, key_name):
        """Нажатие клавиши (enter, esc, tab, space, etc.)"""
        return self.screen.press_key(key_name)

    def hotkey(self, *keys):
        """Выполнение сочетания клавиш"""
        return self.screen.hotkey(*keys)

    def clear_input(self):
        """Очистка поля ввода"""
        return self.screen.clear_input()

    def scroll(self, direction="down", amount=5):
        """Прокрутка страницы/окна"""
        return self.screen.scroll(direction=direction, amount=amount)

    def focus_window(self, title):
        """Активация окна по названию"""
        return self.screen.focus_window(title)

    def minimize_window(self):
        return self.screen.minimize_current_window()

    def maximize_window(self):
        return self.screen.maximize_current_window()

    def close_window(self):
        return self.screen.close_current_window()

    def new_tab(self):
        return self.screen.new_tab()

    def close_tab(self):
        return self.screen.close_tab()

    def send_messenger_message(self, app_keyword, recipient, text, auto_send=False, stealth_background=True):
        """Высокоуровневый сценарий отправки/набора черновика сообщения контакту"""
        return self.screen.send_messenger_message(app_keyword, recipient, text, auto_send=auto_send, stealth_background=stealth_background)

    def get_telegram_chat_names(self):
        """Возвращает список доступных чатов Telegram"""
        return self.screen.get_telegram_chat_names()

    def yandex_search_scenario(self, query):
        """Сценарий поиска в Яндекс"""
        return self.screen.yandex_search(query)

