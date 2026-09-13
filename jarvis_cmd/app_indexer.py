import os
import sys
import re
import glob
import json
import time
import difflib
import subprocess
import urllib.parse
from datetime import datetime

class AppIndexer:
    """
    Интеллектуальный индексатор и постоянная память приложений и Steam-игр для Джарвиса.
    Автоматически находит установленные программы и игры, хранит каталог в JSON
    и поддерживает нечёткий поиск (fuzzy matching) по русским и английским названиям.
    """

    # Предопределенные фонетические синонимы и привязки
    PRESET_ALIASES = {
        "brotato": ["бротато", "братато", "игра бротато", "brotato"],
        "lost light": ["лост лайт", "лостлайт", "игра лост лайт", "lost light"],
        "visual studio code": ["код", "вс код", "вскод", "vs code", "vscode", "студия", "visual studio"],
        "браузер opera gx": ["опера", "опера гх", "opera gx", "opera", "браузер", "интернет"],
        "opera gx": ["опера", "опера гх", "opera gx", "opera", "браузер"],
        "virtualdj": ["виртуал диджей", "виртуал дж", "virtualdj", "virtual dj", "диджей", "пульт"],
        "telegram": ["телеграм", "телега", "тг", "telegram", "телеграмм", "телеграмма", "телеграммы", "миллиграмм", "миллиграмма"],
        "obsidian": ["обсидиан", "заметки", "конспекты", "база знаний", "obsidian"],
        "яндекс музыка": ["музыка", "яндекс музыка", "песни", "треки", "yandex music"],
        "яндекс": ["яндекс", "поиск", "yandex"],
        "яндекс.диск": ["яндекс диск", "диск", "облако яндекс"],
        "zona": ["зона", "фильмы", "сериалы", "кино", "zona"],
        "kmplayer 64x": ["плеер", "кмплеер", "видеоплеер", "kmplayer", "фильм"],
        "amneziavpn": ["амнезия", "впн", "vpn", "amnezia"],
        "adguard vpn": ["адгуард", "адгвард", "adguard"],
        "zoom workplace": ["зум", "конференция", "zoom"],
        "µtorrent": ["торрент", "скачать", "torrent", "utorrent"],
        "битрикс24": ["битрикс", "битрикс24", "bitrix", "bitrix24", "работа"],
        "finale3d": ["финале", "финал", "салюты", "фейерверк", "finale3d"],
        "sunlite suite 2": ["санлайт", "свет", "санлайт сьют", "sunlite"],
        "lesta game center": ["леста", "танки", "ворлд оф тэнкс", "мир танков", "lesta"],
        "rockstar games launcher": ["рокстар", "гта", "рокстар геймс", "rockstar"],
        "проводник": ["проводник", "папки", "файлы", "мои документы", "explorer"],
        "диспетчер задач": ["диспетчер задач", "диспетчер", "процессы", "taskmgr"],
        "калькулятор": ["калькулятор", "посчитай", "calc", "calculator"],
        "блокнот": ["блокнот", "текстовик", "notepad"],
        "стим": ["стим", "steam", "игры"],
        "antigravity": ["антигравити", "гравити", "анти гравити", "antigravity", "откроете гравити", "среда разработки"]
    }

    # Исключения из меню Пуск (деинсталляторы и служебные файлы)
    IGNORE_KEYWORDS = [
        "uninstall", "удалить", "деинсталл", "deinstall", "help", "справка", 
        "readme", "прочти", "license", "setup", "install", "ссылка", "manual"
    ]

    def __init__(self, data_dir=None):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.catalog_path = os.path.join(self.data_dir, "app_catalog.json")
        self.catalog = {}
        self.load_catalog()

    def load_catalog(self):
        """Загружает сохраненный каталог из JSON файла"""
        if os.path.exists(self.catalog_path):
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    self.catalog = json.load(f)
                return True
            except Exception as e:
                print(f"[AppIndexer] Ошибка чтения каталога: {e}")
        self.catalog = {}
        return False

    def save_catalog(self):
        """Сохраняет текущий каталог в JSON файл"""
        try:
            with open(self.catalog_path, "w", encoding="utf-8") as f:
                json.dump(self.catalog, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[AppIndexer] Ошибка сохранения каталога: {e}")
            return False

    def scan_steam_games(self):
        """
        Сканирует библиотеки Steam (libraryfolders.vdf) на всех дисках
        и извлекает все установленные игры из appmanifest_*.acf
        """
        games = {}
        default_steam = r"C:\Program Files (x86)\Steam"
        lib_dirs = [default_steam]

        vdf_path = os.path.join(default_steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Поиск всех путей библиотек
                paths = re.findall(r'"path"\s+"([^"]+)"', content)
                for p in paths:
                    p = p.replace("\\\\", "\\")
                    if os.path.exists(p) and p not in lib_dirs:
                        lib_dirs.append(p)
            except Exception as e:
                print(f"[AppIndexer] Ошибка чтения Steam VDF: {e}")

        # Обход всех найденных библиотек Steam
        for lib in lib_dirs:
            manifest_pattern = os.path.join(lib, "steamapps", "appmanifest_*.acf")
            for mf in glob.glob(manifest_pattern):
                try:
                    with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                        txt = f.read()
                    appid_match = re.search(r'"appid"\s+"(\d+)"', txt)
                    name_match = re.search(r'"name"\s+"([^"]+)"', txt)
                    installdir_match = re.search(r'"installdir"\s+"([^"]+)"', txt)

                    if appid_match and name_match:
                        appid = appid_match.group(1)
                        name = name_match.group(1)
                        installdir = installdir_match.group(1) if installdir_match else ""

                        # Пропускаем служебные пакеты Steam
                        if "redistributable" in name.lower() or "steamworks" in name.lower():
                            continue

                        games[name] = {
                            "canonical_name": name,
                            "type": "steam",
                            "appid": appid,
                            "target": f"steam://rungameid/{appid}",
                            "install_dir": os.path.join(lib, "steamapps", "common", installdir),
                            "aliases": self._generate_game_aliases(name)
                        }
                except Exception as e:
                    print(f"[AppIndexer] Ошибка парсинга манифеста {mf}: {e}")

        print(f"[AppIndexer] [Steam] Найдено игр в Steam: {len(games)}")
        return games

    def _generate_game_aliases(self, name):
        """Генерирует умные синонимы и транслит для игры"""
        norm = name.lower().strip()
        aliases = [norm, f"игра {norm}"]

        # Проверяем предопределенные синонимы
        if norm in self.PRESET_ALIASES:
            aliases.extend(self.PRESET_ALIASES[norm])

        # Удаление спецсимволов для чистого совпадения
        clean = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', norm).strip()
        if clean and clean not in aliases:
            aliases.append(clean)

        return list(set(aliases))

    def scan_windows_shortcuts(self):
        """
        Сканирует ярлыки рабочего стола и меню «Пуск»
        """
        apps = {}
        folders_to_scan = [
            # Рабочий стол текущего пользователя
            os.path.join(os.path.expanduser("~"), "Desktop"),
            # Общий рабочий стол
            r"C:\Users\Public\Desktop",
            # Меню Пуск пользователя
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
            # Общее меню Пуск
            os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
        ]

        for folder in folders_to_scan:
            if not os.path.exists(folder):
                continue

            for root, _, files in os.walk(folder):
                for file in files:
                    if not file.lower().endswith((".lnk", ".url")):
                        continue

                    # Проверка на служебные/деинсталляторы
                    base_name = os.path.splitext(file)[0].strip()
                    low_base = base_name.lower()

                    if any(ign in low_base for ign in self.IGNORE_KEYWORDS):
                        continue

                    # Убираем суффиксы ярлыка
                    clean_name = re.sub(r'\s*—\s*ярлык$', '', base_name, flags=re.IGNORECASE).strip()
                    clean_name = re.sub(r'\s*-\s*ярлык$', '', clean_name, flags=re.IGNORECASE).strip()

                    full_path = os.path.join(root, file)

                    if clean_name not in apps:
                        apps[clean_name] = {
                            "canonical_name": clean_name,
                            "type": "shortcut",
                            "target": full_path,
                            "aliases": self._generate_app_aliases(clean_name)
                        }

        print(f"[AppIndexer] [Apps] Найдено ярлыков программ: {len(apps)}")
        return apps

    def _generate_app_aliases(self, name):
        """Генерирует синонимы для названий программ"""
        norm = name.lower().strip()
        aliases = [norm]

        # Пресеты
        if norm in self.PRESET_ALIASES:
            aliases.extend(self.PRESET_ALIASES[norm])

        # Упрощенная очищенная версия
        clean = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', ' ', norm)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean and clean not in aliases:
            aliases.append(clean)

        # Добавляем ключевые слова без версий (e.g. 'VirtualDJ 2024' -> 'virtualdj')
        words = clean.split()
        if len(words) > 1 and not words[0].isdigit():
            if len(words[0]) >= 3:
                aliases.append(words[0])

        return list(set(aliases))

    def get_system_tools(self):
        """Системные приложения Windows"""
        return {
            "Проводник": {
                "canonical_name": "Проводник",
                "type": "system",
                "target": "explorer.exe",
                "aliases": ["проводник", "папка", "файлы", "explorer"]
            },
            "Диспетчер задач": {
                "canonical_name": "Диспетчер задач",
                "type": "system",
                "target": "taskmgr.exe",
                "aliases": ["диспетчер задач", "диспетчер", "процессы", "taskmgr"]
            },
            "Калькулятор": {
                "canonical_name": "Калькулятор",
                "type": "system",
                "target": "calc.exe",
                "aliases": ["калькулятор", "посчитай", "calc"]
            },
            "Блокнот": {
                "canonical_name": "Блокнот",
                "type": "system",
                "target": "notepad.exe",
                "aliases": ["блокнот", "notepad"]
            },
            "Стим": {
                "canonical_name": "Стим",
                "type": "system",
                "target": "steam://",
                "aliases": ["стим", "steam"]
            }
        }

    def rescan_all(self):
        """
        Полное пересканирование Steam и Windows.
        Объединяет новые находки с существующим каталогом, сохраняя статистику и кастомные связи.
        """
        print("[AppIndexer] [Scan] Запуск полного сканирования системы...")
        steam_games = self.scan_steam_games()
        shortcuts = self.scan_windows_shortcuts()
        system_tools = self.get_system_tools()

        # Объединяем все источники
        all_discovered = {}
        all_discovered.update(system_tools)
        all_discovered.update(shortcuts)
        all_discovered.update(steam_games)

        # Сохраняем пользовательские настройки и статистику
        for name, entry in all_discovered.items():
            if name in self.catalog:
                existing = self.catalog[name]
                # Сохраняем пользовательские синонимы
                custom_aliases = existing.get("custom_aliases", [])
                entry["custom_aliases"] = custom_aliases
                entry["aliases"] = list(set(entry.get("aliases", []) + custom_aliases))
                entry["launch_count"] = existing.get("launch_count", 0)
                entry["last_launched"] = existing.get("last_launched", None)
            else:
                entry["launch_count"] = 0
                entry["last_launched"] = None
                entry["custom_aliases"] = []

            self.catalog[name] = entry

        self.save_catalog()
        print(f"[AppIndexer] [OK] Сканирование завершено. Всего в каталоге: {len(self.catalog)} приложений и игр.")
        return len(self.catalog)

    def learn(self, alias, target, canonical_name=None):
        """
        Обучение Джарвиса новой программе, файлу или связке.
        Например: learn("моя игра", "D:\\Games\\Game.exe")
        """
        alias_clean = alias.lower().strip()
        name = canonical_name or alias.capitalize()

        if name in self.catalog:
            entry = self.catalog[name]
            if "custom_aliases" not in entry:
                entry["custom_aliases"] = []
            if alias_clean not in entry["custom_aliases"]:
                entry["custom_aliases"].append(alias_clean)
            if alias_clean not in entry["aliases"]:
                entry["aliases"].append(alias_clean)
            if target:
                entry["target"] = target
        else:
            self.catalog[name] = {
                "canonical_name": name,
                "type": "custom",
                "target": target,
                "aliases": [alias_clean],
                "custom_aliases": [alias_clean],
                "launch_count": 0,
                "last_launched": None
            }

        self.save_catalog()
        print(f"[AppIndexer] [Learn] Джарвис запомнил: '{alias_clean}' -> '{target}' ({name})")
        return True

    def find_app(self, query):
        """
        Интеллектуальный поиск приложения в каталоге.
        Применяет 3 уровня проверки:
        1. Точное совпадение по имени или синонимам.
        2. Поиск по подстрокам.
        3. Нечёткое соответствие (fuzzy matching) с учетом частоты запусков.
        """
        q = query.lower().strip()
        if not q:
            return None

        # Убираем мусорные вводные слова
        q = re.sub(r'^(игру|программу|приложение|файл|софт)\s+', '', q).strip()

        # 1. Точное совпадение
        for name, item in self.catalog.items():
            if q == name.lower():
                return item
            if q in [a.lower() for a in item.get("aliases", [])]:
                return item

        # 2. Подстрока (если запрос содержится в синониме или наоборот)
        candidates = []
        for name, item in self.catalog.items():
            aliases = [name.lower()] + [a.lower() for a in item.get("aliases", [])]
            for a in aliases:
                if q in a or a in q:
                    candidates.append((item, len(a), item.get("launch_count", 0)))
                    break

        if candidates:
            # Сортируем: сначала те, у кого длина совпадения ближе к запросу, и по популярности
            candidates.sort(key=lambda x: (x[2], -abs(len(q) - x[1])), reverse=True)
            return candidates[0][0]

        # 3. Нечёткое сравнение (Fuzzy matching через SequenceMatcher)
        all_aliases_map = {}
        for name, item in self.catalog.items():
            for a in [name.lower()] + [al.lower() for al in item.get("aliases", [])]:
                all_aliases_map[a] = item

        best_score = 0.0
        best_item = None
        for alias_str, item in all_aliases_map.items():
            score = difflib.SequenceMatcher(None, q, alias_str).ratio()
            if score > best_score:
                best_score = score
                best_item = item

        # Порог уверенности нечеткого сопоставления
        if best_score >= 0.65:
            return best_item

        return None

    def launch(self, query_or_name):
        """
        Запускает найденное приложение или игру без всплывающих консольных окон.
        Обновляет счетчик запусков.
        Возвращает (успех: bool, каноническое_имя: str, описание: str)
        """
        app = self.find_app(query_or_name)
        if not app:
            return False, query_or_name, "Приложение не найдено в каталоге"

        target = app.get("target")
        app_type = app.get("type", "shortcut")
        canonical_name = app.get("canonical_name", query_or_name)

        try:
            import ctypes
            working_dir = None
            args = ""
            launch_target = target

            # 1. Если это ярлык .lnk, извлекаем реальный путь и рабочую директорию
            if target.lower().endswith(".lnk"):
                try:
                    import comtypes.client
                    sh = comtypes.client.CreateObject("WScript.Shell")
                    sc = sh.CreateShortcut(target)
                    real_target = sc.TargetPath
                    real_args = sc.Arguments
                    real_dir = sc.WorkingDirectory
                    if real_target and os.path.exists(real_target):
                        launch_target = real_target
                        args = real_args or ""
                        working_dir = real_dir or os.path.dirname(real_target)
                except Exception:
                    pass

            if not working_dir and os.path.isfile(launch_target):
                working_dir = os.path.dirname(launch_target)

            # 2. Запуск с гарантированным отображением окна (SW_SHOWNORMAL = 1)
            if app_type == "steam":
                os.startfile(target)
            else:
                ret = ctypes.windll.shell32.ShellExecuteW(None, 'open', launch_target, args, working_dir, 1)
                if ret <= 32:
                    os.startfile(target)

            # Обновление статистики
            app["launch_count"] = app.get("launch_count", 0) + 1
            app["last_launched"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_catalog()

            print(f"[AppIndexer] [Launch] Успешно запущено: '{canonical_name}' ({target})")
            return True, canonical_name, f"Запущено: {canonical_name}"

        except Exception as e:
            print(f"[AppIndexer Error] Сбой запуска {canonical_name}: {e}")
            return False, canonical_name, str(e)

    def close(self, query_or_name):
        """
        Закрывает запущенное приложение по запросу
        """
        app = self.find_app(query_or_name)
        canonical_name = app.get("canonical_name", query_or_name) if app else query_or_name

        # Поиск процессов по имени
        import psutil
        closed_count = 0
        search_terms = [canonical_name.lower()]
        if app:
            search_terms.extend([a.lower() for a in app.get("aliases", [])])

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                for term in search_terms:
                    # Сравнение без .exe
                    term_clean = term.replace(".exe", "").strip()
                    if term_clean in pname or pname.replace(".exe", "") in term_clean:
                        proc.terminate()
                        closed_count += 1
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if closed_count > 0:
            print(f"[AppIndexer] [Close] Закрыто процессов ({canonical_name}): {closed_count}")
            return True, canonical_name, f"Закрыто {closed_count} процессов"

        return False, canonical_name, "Процесс не найден среди активных"
