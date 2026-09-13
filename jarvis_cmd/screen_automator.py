import os
import sys
import time
import subprocess
import webbrowser
import urllib.parse
import ctypes
from ctypes import wintypes
import psutil
import pyautogui
import pyperclip
import uiautomation as auto

# Настройка pyautogui (отключаем сбой при нахождении мыши в углу экрана)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

def safe_print(msg):
    """Безопасный вывод в консоль без падений на эмодзи и спецсимволах Windows cp1251"""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            enc = sys.stdout.encoding or 'utf-8'
            print(str(msg).encode(enc, errors='replace').decode(enc))
        except Exception:
            print(str(msg).encode('ascii', errors='replace').decode('ascii'))

class ScreenAutomator:
    """
    Модуль взаимодействия с экраном и элементами интерфейса Windows (Screen & UI Automation).
    Позволяет находить элементы по тексту, кликать, безопасно вводить русский текст
    и выполнять комплексные сценарии (отправка сообщений, управление браузером и окнами).
    """

    def __init__(self):
        pass

    # =========================================================================
    # 1. БЕЗОПАСНЫЙ ВВОД ТЕКСТА И КЛАВИАТУРА
    # =========================================================================

    def type_text(self, text, press_enter=False, delay=0.1):
        """
        Безопасный ввод любого текста (русский язык, спецсимволы, эмодзи).
        Использует буфер обмена (pyperclip) + Ctrl+V, что предотвращает баг с '???' в Windows.
        """
        self._ensure_desktop()
        try:
            # Сохраняем исходный буфер обмена
            old_clip = pyperclip.paste()
        except Exception:
            old_clip = ""

        try:
            pyperclip.copy(text)
            time.sleep(delay)

            # Нативная вставка через Win32 keybd_event (работает надежнее pyautogui)
            VK_CONTROL = 0x11
            VK_V = 0x56
            VK_RETURN = 0x0D
            KEYEVENTF_KEYUP = 0x0002

            user32 = ctypes.windll.user32
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)

            if press_enter:
                time.sleep(0.1)
                user32.keybd_event(VK_RETURN, 0, 0, 0)
                time.sleep(0.05)
                user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

            safe_print(f"[ScreenAutomator] Введен текст: «{text[:30]}...» (Enter={press_enter})")
            return True
        except Exception as e:
            safe_print(f"[ScreenAutomator Error] Ошибка ввода текста: {e}")
            return False
        finally:
            # Восстанавливаем буфер обмена через небольшую паузу
            def restore():
                time.sleep(1.0)
                try:
                    pyperclip.copy(old_clip)
                except Exception:
                    pass
            import threading
            threading.Thread(target=restore, daemon=True).start()

    def press_key(self, key_name):
        """Нажатие отдельной клавиши: enter, esc, tab, space, backspace, up, down, etc."""
        k = key_name.lower().strip()
        key_aliases = {
            "энтер": "enter",
            "эскейп": "esc",
            "таб": "tab",
            "пробел": "space",
            "стереть": "backspace",
            "удалить": "delete",
            "вниз": "down",
            "вверх": "up",
            "влево": "left",
            "вправо": "right"
        }
        actual_key = key_aliases.get(k, k)
        try:
            pyautogui.press(actual_key)
            print(f"[ScreenAutomator] Нажата клавиша: {actual_key}")
            return True
        except Exception as e:
            print(f"[ScreenAutomator Error] Ошибка клавиши {actual_key}: {e}")
            return False

    def hotkey(self, *keys):
        """Выполнение комбинации горячих клавиш: hotkey('ctrl', 'w')"""
        try:
            pyautogui.hotkey(*keys)
            print(f"[ScreenAutomator] Горячие клавиши: {keys}")
            return True
        except Exception as e:
            print(f"[ScreenAutomator Error] Ошибка hotkey {keys}: {e}")
            return False

    def clear_input(self):
        """Очистка текущего поля ввода (Ctrl+A -> Backspace)"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.press('backspace')
            return True
        except Exception as e:
            print(f"[ScreenAutomator Error] Ошибка clear_input: {e}")
            return False

    # =========================================================================
    # 2. УПРАВЛЕНИЕ МЫШЬЮ И ЭКРАНОМ
    # =========================================================================

    def click_current(self):
        """Клик мыши в текущих координатах"""
        pyautogui.click()
        return True

    def double_click_current(self):
        """Двойной клик в текущих координатах"""
        pyautogui.doubleClick()
        return True

    def right_click_current(self):
        """Правый клик в текущих координатах (контекстное меню)"""
        pyautogui.rightClick()
        return True

    def click_at(self, x, y, clicks=1, button="left"):
        """Клик по конкретным экранным координатам"""
        try:
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            return True
        except Exception as e:
            print(f"[ScreenAutomator Error] Ошибка click_at ({x},{y}): {e}")
            return False

    def scroll(self, direction="down", amount=5):
        """Прокрутка колеса мыши: down или up"""
        clicks = -amount if direction == "down" else amount
        try:
            # В Windows pyautogui.scroll принимает число шагов
            pyautogui.scroll(clicks * 120)
            print(f"[ScreenAutomator] Прокрутка: {direction} ({amount})")
            return True
        except Exception as e:
            print(f"[ScreenAutomator Error] Ошибка scroll: {e}")
            return False

    # =========================================================================
    # 3. ПОИСК И КЛИК ПО ЭЛЕМЕНТАМ ИНТЕРФЕЙСА (UI AUTOMATION)
    # =========================================================================

    def find_and_click_element(self, element_name, search_depth=10, max_time=3.0):
        """
        Интеллектуальный поиск элемента (кнопка, ссылка, пункт меню, поле)
        в активном окне или на рабочем столе по названию и клик по нему.
        """
        name_clean = element_name.lower().strip()
        print(f"[ScreenAutomator] Поиск элемента: «{name_clean}»")

        # 1. Сначала ищем в текущем активном окне
        focused_window = auto.GetFocusedControl()
        search_root = None
        if focused_window:
            search_root = focused_window.GetTopLevelControl()

        if not search_root:
            search_root = auto.GetRootControl()

        found_control = None

        # Пробуем найти элемент через дерево UIA
        def inspect_control(ctrl, depth=0):
            nonlocal found_control
            if found_control or depth > search_depth:
                return

            c_name = (ctrl.Name or "").lower().strip()
            if c_name and (name_clean == c_name or name_clean in c_name or c_name in name_clean):
                found_control = ctrl
                return

            for child in ctrl.GetChildren():
                inspect_control(child, depth + 1)
                if found_control:
                    return

        inspect_control(search_root)

        if found_control:
            try:
                rect = found_control.BoundingRectangle
                if rect.width() > 0 and rect.height() > 0:
                    cx = rect.left + rect.width() // 2
                    cy = rect.top + rect.height() // 2
                    pyautogui.click(cx, cy)
                    print(f"[ScreenAutomator] [OK] Элемент «{found_control.Name}» нажат в ({cx}, {cy})")
                    return True, found_control.Name
                else:
                    # Попытка через InvokePattern если координаты 0
                    invoke_pattern = found_control.GetInvokePattern()
                    if invoke_pattern:
                        invoke_pattern.Invoke()
                        return True, found_control.Name
            except Exception as e:
                print(f"[ScreenAutomator Error] Ошибка клика по UIA элементу: {e}")

        # 2. Если не найден в активном окне, пробуем верхние окна рабочего стола
        print(f"[ScreenAutomator] Элемент «{name_clean}» не найден через UIA")
        return False, None

    # =========================================================================
    # 4. УПРАВЛЕНИЕ ОКНАМИ
    # =========================================================================

    def _ensure_desktop(self):
        """Гарантирует привязку текущего потока к интерактивному рабочему столу Default"""
        try:
            hdesk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01FF)
            if hdesk:
                ctypes.windll.user32.SetThreadDesktop(hdesk)
        except Exception:
            pass

    def focus_window(self, title_or_app):
        """
        Находит окно по названию, процессу или классу и выводит его на передний план.
        """
        self._ensure_desktop()
        target = title_or_app.lower().strip()
        
        # 1. Поиск через Win32 EnumWindows (по процессу, заголовку или классу)
        found_hwnd = None
        found_title = ""
        
        import psutil
        from ctypes import wintypes
        
        # Получаем PID процессов, совпадающих с target (например 'telegram', 'whatsapp', 'browser')
        matching_pids = set()
        try:
            for p in psutil.process_iter(['pid', 'name']):
                p_name = (p.info['name'] or "").lower()
                if target in p_name or (target in ["тг", "телеге", "телеграм"] and "telegram" in p_name):
                    matching_pids.add(p.info['pid'])
        except Exception:
            pass

        candidate_by_pid = None
        candidate_by_title = None

        def callback(hwnd, extra):
            nonlocal candidate_by_pid, candidate_by_title
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
                
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.lower()
            
            cbuf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, cbuf, 256)
            cls_name = cbuf.value.lower()
            
            # Приоритет 1: Прямое совпадение по процессу (Telegram.exe, WhatsApp.exe)
            if pid.value in matching_pids and buff.value and not candidate_by_pid:
                candidate_by_pid = (hwnd, buff.value)
                return False # Нашли прямое окно приложения, останавливаемся
            
            # Приоритет 2: Совпадение по заголовку или классу
            if (target in title or target in cls_name) and buff.value and not candidate_by_title:
                candidate_by_title = (hwnd, buff.value)

            return True

        CB_FUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        ctypes.windll.user32.EnumWindows(CB_FUNC(callback), 0)

        chosen = candidate_by_pid or candidate_by_title
        if chosen:
            found_hwnd, found_title = chosen
            self.last_focused_hwnd = found_hwnd

        if found_hwnd:
            try:
                ctypes.windll.user32.ShowWindow(found_hwnd, 9) # SW_RESTORE
                ctypes.windll.user32.SetWindowPos(found_hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
                time.sleep(0.05)
                ctypes.windll.user32.SetWindowPos(found_hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
                ctypes.windll.user32.BringWindowToTop(found_hwnd)
                ctypes.windll.user32.SetForegroundWindow(found_hwnd)
                time.sleep(0.3)
                safe_print(f"[ScreenAutomator] [OK] Активировано окно HWND={found_hwnd}: «{found_title}»")
                return True
            except Exception as e:
                safe_print(f"[ScreenAutomator Error] Ошибка активации HWND {found_hwnd}: {e}")

        # 2. Попытка через UI Automation
        root = auto.GetRootControl()
        for win in root.GetChildren():
            w_name = (win.Name or "").lower()
            c_name = (win.ClassName or "").lower()
            if target in w_name or target in c_name:
                try:
                    win.SetActive()
                    win.SetFocus()
                    time.sleep(0.2)
                    safe_print(f"[ScreenAutomator] Активировано окно UIA: «{win.Name}»")
                    return True
                except Exception:
                    pass

        # 3. Резервный запуск если окно свернуто в трей
        try:
            if target in ["telegram", "тг", "телеграм"]:
                os.startfile(r"C:\Users\bear_\AppData\Roaming\Telegram Desktop\Telegram.exe")
                time.sleep(1.0)
                return True
        except Exception:
            pass

        return False

    def minimize_current_window(self):
        """Сворачивает текущее окно (Win+Down)"""
        pyautogui.hotkey('win', 'down')
        return True

    def maximize_current_window(self):
        """Разворачивает текущее окно (Win+Up)"""
        pyautogui.hotkey('win', 'up')
        return True

    def close_current_window(self):
        """Закрывает текущее окно (Alt+F4)"""
        pyautogui.hotkey('alt', 'f4')
        return True

    def close_tab(self):
        """Закрывает текущую вкладку в браузере или редакторе (Ctrl+W)"""
        pyautogui.hotkey('ctrl', 'w')
        return True

    def new_tab(self):
        """Открывает новую вкладку (Ctrl+T)"""
        pyautogui.hotkey('ctrl', 't')
        return True

    # =========================================================================
    # 5. ВЫСОКОУРОВНЕВЫЕ СЦЕНАРИИ
    # =========================================================================

    def _find_telegram_hwnd(self):
        """Находит HWND главного окна Telegram Desktop"""
        self._ensure_desktop()
        user32 = ctypes.windll.user32
        windows = []
        def cb(hwnd, lparam):
            try:
                length = user32.GetWindowTextLengthW(hwnd)
                tbuff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, tbuff, length + 1)
                cbuff = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cbuff, 256)
                vis = user32.IsWindowVisible(hwnd)
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                windows.append((hwnd, vis, pid.value, cbuff.value, tbuff.value))
            except Exception:
                pass
            return True
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(cb), 0)

        # Приоритет 1: главный класс окна Qt Telegram
        for h, v, pid, c, t in windows:
            if 'qt51519qwindowicon' in c.lower() or 'telegramuserdata' in c.lower():
                return h
        # Приоритет 2: заголовок или имя процесса
        for h, v, pid, c, t in windows:
            if 'tray' not in c.lower() and 'media' not in c.lower() and 'ime' not in c.lower():
                if 'telegram' in t.lower() or 'telegram' in c.lower():
                    return h
        return None

    def get_telegram_chat_names(self):
        """Возвращает список доступных названий чатов в Telegram Desktop"""
        self._ensure_desktop()
        tg_hwnd = self._find_telegram_hwnd()
        if not tg_hwnd:
            return []
        try:
            tg = auto.ControlFromHandle(tg_hwnd)
            names = []
            for c, d in auto.WalkControl(tg, maxDepth=8):
                if c.ControlTypeName == 'ListItemControl' and c.Name:
                    raw = c.Name.split(',')[0].strip()
                    if raw and raw not in names:
                        names.append(raw)
            return names
        except Exception:
            return []

    def _send_telegram_message(self, recipient, message_text, auto_send=False, stealth_background=True):
        """
        Надежный сценарий набора/отправки сообщения в Telegram Desktop через UI Automation и Win32.
        - Если auto_send=False: текст вставляется в поле ввода как черновик, без нажатия Enter.
        - Если auto_send=True: отправляется нажатием Enter.
        """
        self._ensure_desktop()
        user32 = ctypes.windll.user32
        prev_fg = user32.GetForegroundWindow()
        pt = (ctypes.c_long * 2)()
        user32.GetCursorPos(pt)
        prev_cursor = (pt[0], pt[1])

        tg_hwnd = self._find_telegram_hwnd()
        if not tg_hwnd:
            try:
                os.startfile(r"C:\Users\bear_\AppData\Roaming\Telegram Desktop\Telegram.exe")
                time.sleep(1.5)
                tg_hwnd = self._find_telegram_hwnd()
            except Exception:
                pass

        if not tg_hwnd:
            safe_print("[ScreenAutomator Error] Окно Telegram Desktop не найдено.")
            return False

        # Активация окна Telegram
        user32.ShowWindow(tg_hwnd, 9) # SW_RESTORE
        user32.SetWindowPos(tg_hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        time.sleep(0.05)
        user32.SetWindowPos(tg_hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002)
        user32.BringWindowToTop(tg_hwnd)
        user32.SetForegroundWindow(tg_hwnd)
        time.sleep(0.3)

        tg = auto.ControlFromHandle(tg_hwnd)

        # 1. Поиск контакта в списке чатов через UI Automation
        target_chat = None
        import re
        recip_clean = re.sub(r'[^\w\s]', '', recipient).lower().strip()
        recip_words = [w for w in recip_clean.split() if len(w) > 1]
        
        expanded_words = set(recip_words)
        for w in list(expanded_words):
            if 'саня' in w: expanded_words.add('саша')
            if 'саша' in w: expanded_words.add('саня')
            if 'жена' in w: expanded_words.add('жене')
            if 'жене' in w: expanded_words.add('жена')
            if 'дима' in w: expanded_words.add('дмитрий')

        for c, d in auto.WalkControl(tg, maxDepth=8):
            if c.ControlTypeName == 'ListItemControl' and c.Name:
                c_clean = re.sub(r'[^\w\s]', '', c.Name).lower()
                # Не путать с чатом самого бота управления
                if "j.a.r.v.i.s" in c_clean and not any("джарвис" in w for w in expanded_words):
                    continue
                matched = sum(1 for w in expanded_words if w in c_clean)
                if matched >= 1:
                    target_chat = c
                    safe_print(f"[ScreenAutomator] Найден контакт в списке: «{c.Name.split(',')[0]}»")
                    break

        if target_chat:
            inv = target_chat.GetInvokePattern()
            if inv:
                inv.Invoke()
            else:
                sel = target_chat.GetSelectionItemPattern()
                if sel: sel.Select()
            time.sleep(0.4)
        else:
            # Резервный поиск через поисковую строку Telegram
            safe_print(f"[ScreenAutomator] Контакт «{recipient}» не в верхнем списке, поиск через строку поиска...")
            search_box = None
            for c, d in auto.WalkControl(tg, maxDepth=6):
                if c.ControlTypeName == 'EditControl' and c.BoundingRectangle.bottom < 400:
                    search_box = c
                    break
            if search_box:
                r = search_box.BoundingRectangle
                cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
                user32.SetCursorPos(cx, cy)
                time.sleep(0.05)
                user32.mouse_event(0x0002, 0, 0, 0, 0)
                time.sleep(0.05)
                user32.mouse_event(0x0004, 0, 0, 0, 0)
                time.sleep(0.1)
                pyperclip.copy(recipient)
                user32.keybd_event(0x11, 0, 0, 0)
                user32.keybd_event(0x56, 0, 0, 0)
                time.sleep(0.05)
                user32.keybd_event(0x56, 0, 2, 0)
                user32.keybd_event(0x11, 0, 2, 0)
                time.sleep(0.6)
                user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.05)
                user32.keybd_event(0x0D, 0, 2, 0)
                time.sleep(0.4)

        # 2. Находим поле ввода сообщения (EditControl внизу окна)
        msg_box = None
        for c, d in auto.WalkControl(tg, maxDepth=8):
            if c.ControlTypeName == 'EditControl' and c.BoundingRectangle.bottom > 800:
                msg_box = c
                break

        if not msg_box:
            from ctypes import wintypes
            r = wintypes.RECT()
            user32.GetWindowRect(tg_hwnd, ctypes.byref(r))
            cx = r.left + int((r.right - r.left) * 0.65)
            cy = r.bottom - 45
        else:
            r = msg_box.BoundingRectangle
            cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2

        user32.SetCursorPos(cx, cy)
        time.sleep(0.05)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(0.15)

        # Очистка поля
        user32.keybd_event(0x11, 0, 0, 0)
        user32.keybd_event(0x41, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x41, 0, 2, 0)
        user32.keybd_event(0x11, 0, 2, 0)
        time.sleep(0.05)
        user32.keybd_event(0x08, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x08, 0, 2, 0)
        time.sleep(0.1)

        # Ввод текста через буфер обмена
        pyperclip.copy(message_text)
        user32.keybd_event(0x11, 0, 0, 0)
        user32.keybd_event(0x56, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x56, 0, 2, 0)
        user32.keybd_event(0x11, 0, 2, 0)
        time.sleep(0.2)

        # Отправка или режим черновика
        if auto_send:
            time.sleep(0.1)
            user32.keybd_event(0x0D, 0, 0, 0) # Enter
            time.sleep(0.05)
            user32.keybd_event(0x0D, 0, 2, 0)
            safe_print(f"[ScreenAutomator] [OK] Сообщение для «{recipient}» успешно отправлено!")
        else:
            safe_print(f"[ScreenAutomator] [OK] Текст сообщения для «{recipient}» набран как черновик (НЕ отправлено).")

        # 3. Возврат состояния пользователя
        if stealth_background:
            time.sleep(0.2)
            user32.ShowWindow(tg_hwnd, 6) # SW_MINIMIZE
            if prev_fg and prev_fg != tg_hwnd:
                user32.SetForegroundWindow(prev_fg)
            user32.SetCursorPos(prev_cursor[0], prev_cursor[1])

        return True

    def send_messenger_message(self, app_keyword, recipient, message_text, auto_send=False, stealth_background=True):
        """
        Сценарий: отправка сообщения контакту в мессенджере (Telegram, VK, WhatsApp, Битрикс24 и др.)
        В режиме auto_send=False (по умолчанию) вводит сообщение как черновик, не отправляя.
        """
        self._ensure_desktop()
        safe_print(f"[ScreenAutomator] [Action] Сценарий мессенджера: [{app_keyword}] -> {recipient}: «{message_text}» (AutoSend={auto_send})")

        app_clean = (app_keyword or "telegram").lower().strip()
        if app_clean in ["telegram", "тг", "телеграм", "телеге"]:
            return self._send_telegram_message(recipient, message_text, auto_send=auto_send, stealth_background=stealth_background)

        # Резервный сценарий для сторонних мессенджеров (WhatsApp, VK и т.д.)
        prev_fg = ctypes.windll.user32.GetForegroundWindow()
        pt = (ctypes.c_long * 2)()
        ctypes.windll.user32.GetCursorPos(pt)
        prev_cursor = (pt[0], pt[1])

        activated = self.focus_window(app_clean)
        if not activated:
            try:
                os.startfile(app_clean)
                time.sleep(2.0)
                self.focus_window(app_clean)
            except Exception:
                pass

        time.sleep(0.3)
        fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.3)
        self.clear_input()
        time.sleep(0.1)
        self.type_text(recipient, press_enter=False)
        time.sleep(0.7)
        pyautogui.press('enter')
        time.sleep(0.4)

        from ctypes import wintypes
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
        if rect.right > rect.left and rect.bottom > rect.top:
            input_x = rect.left + int((rect.right - rect.left) * 0.65)
            input_y = rect.bottom - 45
            ctypes.windll.user32.SetCursorPos(input_x, input_y)
            time.sleep(0.08)
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
            time.sleep(0.2)

        self.type_text(message_text, press_enter=auto_send)

        if stealth_background and fg_hwnd:
            time.sleep(0.2)
            ctypes.windll.user32.ShowWindow(fg_hwnd, 6)
            if prev_fg and prev_fg != fg_hwnd:
                ctypes.windll.user32.SetForegroundWindow(prev_fg)
            ctypes.windll.user32.SetCursorPos(prev_cursor[0], prev_cursor[1])

        return True

    def yandex_search(self, query):
        """
        Сценарий: открытие Яндекса и ввод поискового запроса
        """
        url = f"https://ya.ru/search/?text={urllib.parse.quote(query)}"
        webbrowser.open(url)
        print(f"[ScreenAutomator] [OK] Открыт поиск Яндекс по запросу: «{query}»")
        return True
