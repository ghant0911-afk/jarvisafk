import sys
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import subprocess
import shutil

sys.path.insert(0, str(Path(__file__).parent))

from jarvis_cmd.brain import plan_command
from jarvis_cmd.executor import run_command
from jarvis_cmd.safety import check_command


BG = "#060816"
TEXT = "#eef2ff"
MUTED = "#98a3c7"
CYAN = "#5ad1ff"
BLUE = "#4f7cff"
VIOLET = "#9b5cff"
PINK = "#d56dff"
GREEN = "#39d98a"
AMBER = "#ffb14a"
BORDER = "#4d6cff"
PANEL = "#090d1a"
PANEL_ALT = "#0c1224"
LOG_BG = "#07101d"
THINK_BG = "#081326"


class GradientCanvas(tk.Canvas):
    def __init__(self, master, color_stops: list[str], **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.color_stops = color_stops
        self.phase = 0.0
        self.bind("<Configure>", self._draw)

    def _hex_to_rgb(self, value: str):
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def _draw_gradient(self, width: int, height: int):
        segments = max(len(self.color_stops) - 1, 1)
        segment_width = width / segments
        for x in range(width):
            seg = min(int(x / segment_width), segments - 1)
            start = self._hex_to_rgb(self.color_stops[seg])
            end = self._hex_to_rgb(self.color_stops[seg + 1])
            local_x = x - seg * segment_width
            ratio = local_x / max(segment_width, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            self.create_line(x, 0, x, height, fill=self._rgb_to_hex((r, g, b)))

    def _draw_grid(self, width: int, height: int):
        spacing = 72
        offset = int((self.phase * 18) % spacing)
        for x in range(-spacing, width + spacing, spacing):
            self.create_line(x + offset, 0, x + offset, height, fill="#10244d", width=1)
        for y in range(-spacing, height + spacing, spacing):
            self.create_line(0, y + offset, width, y + offset, fill="#0d1d40", width=1)

    def _draw_hologram(self, width: int, height: int):
        cx = width * 0.74
        cy = height * 0.57
        m = __import__('math')
        pulse = 8 * (1 + m.sin(self.phase * 0.05))
        shift = 20 * m.sin(self.phase * 0.025)

        for i, color in enumerate(["#6e45ff", "#4f7cff", "#69d8ff"]):
            radius = 150 + i * 42 + pulse
            self.create_oval(cx - radius, cy - radius + shift * 0.18, cx + radius, cy + radius + shift * 0.18, outline=color, width=2)

        for i in range(4):
            y = cy - 105 + i * 62 + (self.phase * 0.6 % 62)
            self.create_arc(cx - 205, y - 30, cx + 205, y + 30, start=16, extent=146, style=tk.ARC, outline="#79c3ff", width=1)

        for i in range(4):
            angle = self.phase * 0.018 + i * 1.45
            x1 = cx + m.cos(angle) * 52
            y1 = cy + m.sin(angle) * 52
            x2 = cx + m.cos(angle) * 185
            y2 = cy + m.sin(angle) * 185
            self.create_line(x1, y1, x2, y2, fill="#4f7cff", width=2)

        self.create_oval(cx - 42, cy - 42, cx + 42, cy + 42, outline="#7aa7ff", width=2)
        self.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, fill="#8f67ff", outline="#d1b7ff", width=1)

    def _draw_glows(self, width: int, height: int):
        drift = 18 * __import__('math').sin(self.phase * 0.015)
        self.create_oval(width - 360 + drift, -110, width + 40 + drift, 210, fill="#102861", outline="")
        self.create_oval(-100 - drift, -70, 260 - drift, 210, fill="#3c1887", outline="")
        self.create_oval(width // 2 - 150, -50 + drift * 0.2, width // 2 + 150, 140 + drift * 0.2, fill="#24114f", outline="")

    def _draw(self, _event=None):
        self.delete("all")
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        self._draw_gradient(width, height)
        self._draw_glows(width, height)
        self._draw_grid(width, height)
        self._draw_hologram(width, height)

    def animate(self):
        self.phase += 1.0
        self._draw()


class Card(tk.Frame):
    def __init__(self, master, bg_color=PANEL_ALT, border=BORDER, **kwargs):
        super().__init__(master, bg=bg_color, highlightthickness=1, highlightbackground=border, **kwargs)


class OutlineCard(tk.Frame):
    def __init__(self, master, border=BORDER, **kwargs):
        super().__init__(master, bg=BG, highlightthickness=1, highlightbackground=border, **kwargs)


class MetricCard(OutlineCard):
    def __init__(self, master, title: str, value: str, accent: str, width: int = 150, height: int = 86):
        super().__init__(master, width=width, height=height, border=accent)
        self.pack_propagate(False)
        self.value_var = tk.StringVar(value=value)
        self.accent = accent

        top = tk.Frame(self, bg=accent, height=2)
        top.pack(fill=tk.X, side=tk.TOP)
        inner = tk.Frame(self, bg=BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        tk.Label(inner, text=title, fg=MUTED, bg=BG, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(inner, textvariable=self.value_var, fg=TEXT, bg=BG, font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(5, 0))

    def set(self, value: str):
        self.value_var.set(value)


class NeonButton(tk.Button):
    def __init__(self, master, text: str, command, bg_color: str, hover: str, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            bg=bg_color,
            fg=TEXT,
            activebackground=hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=12,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs,
        )
        self.default_bg = bg_color
        self.hover_bg = hover
        self.bind("<Enter>", lambda _e: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda _e: self.configure(bg=self.default_bg))


class JarvisFuturisticUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Jarvis Neon Console")
        self.root.geometry("1440x900")
        self.root.minsize(1220, 780)
        self.root.configure(bg=BG)

        self.mode_var = tk.StringVar(value="safe")
        self.input_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Jarvis shell ready. Futuristic control layer active.")

        self._build_ui()
        self._append_log("Jarvis Neon Console initialized")
        self._append_thought("BOOT", "Система поднята. Готов анализировать запросы.")
        self._append_thought("STATE", "Voice stack пока не подключен к GUI, но planner/safety/execution доступны.")
        self._update_metrics()
        self._animate_background()

    def _build_ui(self) -> None:
        self.bg_canvas = GradientCanvas(self.root, ["#3f1788", "#6928ff", "#2f5dff", "#102047"], bg=BG)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        overlay = tk.Frame(self.root, bg=BG)
        overlay.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        header_shell = tk.Frame(overlay, bg=BG)
        header_shell.pack(fill=tk.X, pady=(0, 12))

        header = Card(header_shell, bg_color="#0b1020")
        header.pack(fill=tk.X)

        header_left = tk.Frame(header, bg="#0b1020")
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=18, pady=16)
        tk.Label(header_left, text="JARVIS", fg="#ffffff", bg="#0b1020", font=("Segoe UI", 31, "bold")).pack(anchor="w")
        tk.Label(header_left, text="Neon command intelligence / purple-blue synthetic core", fg="#d5dbff", bg="#0b1020", font=("Segoe UI", 11)).pack(anchor="w")

        perf_wrap = Card(header, bg_color="#0a0f1d")
        perf_wrap.pack(side=tk.RIGHT, padx=14, pady=14)

        perf_head = tk.Frame(perf_wrap, bg="#0a0f1d")
        perf_head.pack(fill=tk.X, padx=12, pady=(10, 6))
        tk.Label(perf_head, text="PERFORMANCE", fg="#dce4ff", bg="#0a0f1d", font=("Segoe UI", 10, "bold")).pack(anchor="e")
        self.time_label = tk.Label(perf_head, text="--:--:--", fg=CYAN, bg="#0a0f1d", font=("Consolas", 14, "bold"))
        self.time_label.pack(anchor="e")

        perf_cards = tk.Frame(perf_wrap, bg="#0a0f1d")
        perf_cards.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.cpu_card = MetricCard(perf_cards, "CPU", "-- %", CYAN, width=140)
        self.cpu_card.pack(side=tk.LEFT, padx=(0, 8))
        self.ram_card = MetricCard(perf_cards, "RAM", "--", VIOLET, width=180)
        self.ram_card.pack(side=tk.LEFT, padx=(0, 8))
        self.disk_card = MetricCard(perf_cards, "DISK D:", "--", GREEN, width=170)
        self.disk_card.pack(side=tk.LEFT, padx=(0, 8))
        self.ollama_card = MetricCard(perf_cards, "OLLAMA", "--", AMBER, width=140)
        self.ollama_card.pack(side=tk.LEFT)

        body = tk.Frame(overlay, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        sidebar = Card(body, bg_color=PANEL, width=285)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        sidebar.pack_propagate(False)

        main = Card(body, bg_color=PANEL)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar(sidebar)
        self._build_main(main)

    def _section_title(self, master, title: str, subtitle: str = ""):
        tk.Label(master, text=title, fg=TEXT, bg=master["bg"], font=("Segoe UI", 15, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(master, text=subtitle, fg=MUTED, bg=master["bg"], font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 10))

    def _build_sidebar(self, parent: tk.Frame) -> None:
        top = tk.Frame(parent, bg=PANEL)
        top.pack(fill=tk.X, padx=14, pady=14)
        self._section_title(top, "Quick launch", "Сценарии быстрого взаимодействия")

        actions = [
            ("Показать файлы", "покажи файлы", "#1c2a59", "#28408b"),
            ("Текущая папка", "текущая папка", "#30205f", "#50339b"),
            ("Дата и время", "дата и время", "#17346c", "#25559f"),
            ("Открыть блокнот", "запусти notepad", "#40215b", "#65348f"),
            ("Что ты умеешь", "что ты умеешь", "#202949", "#33406d"),
        ]
        for label, text, bg_color, hover in actions:
            NeonButton(top, label, lambda t=text: self._run_input(t), bg_color=bg_color, hover=hover).pack(fill=tk.X, pady=5)

        mode = Card(parent, bg_color=PANEL_ALT)
        mode.pack(fill=tk.X, padx=14, pady=(10, 10))
        tk.Label(mode, text="Execution mode", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        tk.Radiobutton(mode, text="Safe preview", variable=self.mode_var, value="safe", fg="#d9deff", bg=PANEL_ALT, selectcolor=PANEL_ALT, activebackground=PANEL_ALT, activeforeground="#ffffff", font=("Segoe UI", 10)).pack(anchor="w", padx=12)
        tk.Radiobutton(mode, text="Real execution", variable=self.mode_var, value="real", fg="#d9deff", bg=PANEL_ALT, selectcolor=PANEL_ALT, activebackground=PANEL_ALT, activeforeground="#ffffff", font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(3, 10))

        sysbox = Card(parent, bg_color=PANEL_ALT)
        sysbox.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        tk.Label(sysbox, text="Node state", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        self.state_text = tk.Text(sysbox, bg=LOG_BG, fg="#b9c6ee", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 10), height=12)
        self.state_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.state_text.insert("1.0", "PROJECT: D:\\Jarvis\nUI THEME: neon purple-blue\nVOICE: pending audio deps\nPLANNER: fallback + optional ollama\nSAFETY: enabled\nGUI: active\n")
        self.state_text.config(state=tk.DISABLED)

    def _build_main(self, parent: tk.Frame) -> None:
        top = tk.Frame(parent, bg=PANEL)
        top.pack(fill=tk.X, padx=16, pady=(16, 12))
        self._section_title(top, "Command deck", "Вводи запрос, смотри как Jarvis думает и что делает")

        input_row = tk.Frame(top, bg=PANEL)
        input_row.pack(fill=tk.X)
        entry = tk.Entry(input_row, textvariable=self.input_var, bg=LOG_BG, fg=TEXT, insertbackground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 13))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=13)
        entry.bind("<Return>", lambda _e: self._run_input())
        entry.focus_set()

        NeonButton(input_row, "RUN", self._run_input, bg_color="#3769ff", hover="#5082ff", width=10).pack(side=tk.LEFT, padx=(10, 0))
        NeonButton(input_row, "CLEAR", self._clear_log, bg_color="#4a2d83", hover="#6940b4", width=10).pack(side=tk.LEFT, padx=(10, 0))

        middle = tk.Frame(parent, bg=PANEL)
        middle.pack(fill=tk.BOTH, expand=True, padx=16)

        left_col = tk.Frame(middle, bg=PANEL)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        right_col = tk.Frame(middle, bg=PANEL)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        think_box = Card(left_col, bg_color=PANEL_ALT)
        think_box.pack(fill=tk.X, pady=(0, 12))
        tk.Label(think_box, text="Thinking console", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 8))
        self.think_log = scrolledtext.ScrolledText(think_box, bg=THINK_BG, fg="#cbd7ff", insertbackground="#ffffff", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 10), height=10)
        self.think_log.pack(fill=tk.X, padx=12, pady=(0, 12))

        log_box = Card(left_col, bg_color=PANEL_ALT)
        log_box.pack(fill=tk.BOTH, expand=True)
        tk.Label(log_box, text="Live activity", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 8))
        self.log = scrolledtext.ScrolledText(log_box, bg=LOG_BG, fg="#dce4ff", insertbackground="#ffffff", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        plan_box = Card(right_col, bg_color=PANEL_ALT)
        plan_box.pack(fill=tk.BOTH, expand=True)
        tk.Label(plan_box, text="Planner / safety / result", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 8))
        self.details = scrolledtext.ScrolledText(plan_box, bg=LOG_BG, fg="#dce4ff", insertbackground="#ffffff", relief=tk.FLAT, wrap=tk.WORD, font=("Consolas", 10))
        self.details.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        bottom = Card(parent, bg_color=PANEL_ALT)
        bottom.pack(fill=tk.X, padx=16, pady=(12, 16))
        tk.Label(bottom, text="Status stream", fg=TEXT, bg=PANEL_ALT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        tk.Label(bottom, textvariable=self.status_var, fg=CYAN, bg=PANEL_ALT, anchor="w", justify=tk.LEFT, font=("Segoe UI", 10)).pack(fill=tk.X, padx=12)

        pills = tk.Frame(bottom, bg=PANEL_ALT)
        pills.pack(fill=tk.X, padx=12, pady=(10, 12))
        self.mode_pill = self._status_pill(pills, "MODE", self.mode_var.get(), VIOLET)
        self.mode_pill.pack(side=tk.LEFT, padx=(0, 8))
        self._status_pill(pills, "SAFETY", "ENABLED", GREEN).pack(side=tk.LEFT, padx=(0, 8))
        self._status_pill(pills, "VOICE", "PENDING", AMBER).pack(side=tk.LEFT, padx=(0, 8))
        self._status_pill(pills, "PROFILE", "OFFLINE", CYAN).pack(side=tk.LEFT)

    def _status_pill(self, master, title: str, value: str, color: str):
        frame = tk.Frame(master, bg="#0d1326", highlightthickness=1, highlightbackground=BORDER)
        tk.Label(frame, text=title, fg=MUTED, bg="#0d1326", font=("Segoe UI", 8)).pack(anchor="w", padx=10, pady=(7, 1))
        tk.Label(frame, text=value, fg=color, bg="#0d1326", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 7))
        return frame

    def _append_log(self, text: str) -> None:
        self.log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log.see(tk.END)

    def _append_thought(self, stage: str, text: str) -> None:
        self.think_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {stage:<8} :: {text}\n")
        self.think_log.see(tk.END)

    def _set_details(self, text: str) -> None:
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, text)

    def _clear_log(self) -> None:
        self.log.delete("1.0", tk.END)
        self.details.delete("1.0", tk.END)
        self.think_log.delete("1.0", tk.END)
        self.status_var.set("Логи очищены")
        self._append_thought("RESET", "Логи очищены пользователем")

    def _get_cpu_percent(self) -> str:
        try:
            output = subprocess.check_output(["wmic", "cpu", "get", "loadpercentage", "/value"], text=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            for line in output.splitlines():
                if line.startswith("LoadPercentage="):
                    return f"{line.split('=', 1)[1].strip()} %"
        except Exception:
            pass
        return "n/a"

    def _get_ram_usage(self) -> str:
        try:
            output = subprocess.check_output(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/value"], text=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            free_kb = total_kb = None
            for line in output.splitlines():
                if line.startswith("FreePhysicalMemory="):
                    free_kb = int(line.split("=", 1)[1].strip())
                elif line.startswith("TotalVisibleMemorySize="):
                    total_kb = int(line.split("=", 1)[1].strip())
            if free_kb and total_kb:
                used_gb = (total_kb - free_kb) / 1024 / 1024
                total_gb = total_kb / 1024 / 1024
                pct = int(((total_kb - free_kb) / total_kb) * 100)
                return f"{used_gb:.1f}/{total_gb:.1f} GB · {pct}%"
        except Exception:
            pass
        return "n/a"

    def _get_disk_usage(self, path: str = "D:\\") -> str:
        try:
            usage = shutil.disk_usage(path)
            used = (usage.total - usage.free) / 1024 / 1024 / 1024
            total = usage.total / 1024 / 1024 / 1024
            pct = int(((usage.total - usage.free) / usage.total) * 100)
            return f"{used:.1f}/{total:.1f} GB · {pct}%"
        except Exception:
            return "n/a"

    def _get_ollama_state(self) -> str:
        try:
            result = subprocess.run(["where", "ollama"], capture_output=True, text=True, shell=True, creationflags=0x08000000)
            return "ONLINE" if result.returncode == 0 else "OFF"
        except Exception:
            return "UNKNOWN"

    def _update_metrics(self) -> None:
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.cpu_card.set(self._get_cpu_percent())
        self.ram_card.set(self._get_ram_usage())
        self.disk_card.set(self._get_disk_usage())
        self.ollama_card.set(self._get_ollama_state())
        self.mode_pill.winfo_children()[1].config(text=self.mode_var.get().upper())
        self.root.after(1800, self._update_metrics)

    def _animate_background(self) -> None:
        self.bg_canvas.animate()
        self.root.after(60, self._animate_background)

    def _run_input(self, forced_text: str | None = None) -> None:
        text = forced_text if forced_text is not None else self.input_var.get().strip()
        if not text:
            messagebox.showinfo("Jarvis", "Введи запрос или нажми на быструю кнопку.")
            return

        if forced_text is None:
            self.input_var.set("")

        self._append_log(f"You > {text}")
        self._append_thought("INPUT", f"Получен запрос: {text}")
        self._append_thought("PLAN", "Анализирую намерение и подбираю способ действия")

        try:
            plan = plan_command(text)
        except Exception as exc:
            self._append_log(f"Planner error: {exc}")
            self._append_thought("ERROR", f"Ошибка планирования: {exc}")
            self.status_var.set("Ошибка планирования")
            return

        self._append_thought("INTENT", f"intent={plan.intent}; source={plan.source}")
        self._append_thought("REASON", plan.reason)

        if plan.command:
            decision = check_command(plan.command)
            safety = f"allowed={decision.allowed}, confirm={decision.requires_confirmation}, reason={decision.reason}"
            self._append_thought("COMMAND", plan.command)
            self._append_thought("SAFETY", decision.reason)
        else:
            decision = None
            safety = "no command"
            self._append_thought("COMMAND", "Команда не требуется, будет текстовый ответ")

        self._set_details("\n".join([
            f"request: {text}",
            f"source: {plan.source}",
            f"intent: {plan.intent}",
            f"reason: {plan.reason}",
            f"command: {plan.command or '-'}",
            f"safety: {safety}",
            f"mode: {self.mode_var.get()}",
        ]))
        self._append_log(f"Jarvis > {plan.reason}")

        if plan.intent == "answer" or not plan.command:
            self._append_thought("OUTPUT", "Сформирован ответ без запуска системной команды")
            self.status_var.set("Ответ подготовлен")
            return

        if decision and not decision.allowed:
            self._append_log("Blocked by safety policy")
            self._append_thought("BLOCK", "Команда остановлена политикой безопасности")
            self.status_var.set("Команда заблокирована")
            return

        if self.mode_var.get() == "safe":
            self._append_log(f"[preview] would run: {plan.command}")
            self._append_thought("PREVIEW", f"В safe-режиме команда не запускается: {plan.command}")
            self.status_var.set("Safe preview mode")
            return

        if decision and decision.requires_confirmation:
            self._append_thought("CONFIRM", "Ожидается подтверждение пользователя")
            ok = messagebox.askyesno("Подтверждение", f"Команда потенциально рискованная:\n\n{plan.command}\n\nВыполнить?")
            if not ok:
                self._append_log("Execution cancelled")
                self._append_thought("CANCEL", "Пользователь отменил выполнение")
                self.status_var.set("Отменено")
                return

        self._append_log(f"Running: {plan.command}")
        self._append_thought("EXEC", f"Запускаю: {plan.command}")
        result = run_command(plan.command)
        if result.stdout:
            self._append_log("STDOUT:")
            self._append_log(result.stdout)
            self._append_thought("STDOUT", result.stdout[:180])
        if result.stderr:
            self._append_log("STDERR:")
            self._append_log(result.stderr)
            self._append_thought("STDERR", result.stderr[:180])
        self._append_log(f"Exit code: {result.exit_code}")
        self._append_thought("DONE", f"Команда завершена с кодом {result.exit_code}")
        self.status_var.set(f"Команда завершена с кодом {result.exit_code}")


def main() -> None:
    root = tk.Tk()
    JarvisFuturisticUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
