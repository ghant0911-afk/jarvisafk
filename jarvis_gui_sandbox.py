import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from jarvis_cmd.brain import plan_command
from jarvis_cmd.executor import run_command
from jarvis_cmd.safety import check_command


class JarvisSandboxApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Jarvis Sandbox")
        self.root.geometry("980x720")
        self.root.minsize(860, 620)

        self.mode_var = tk.StringVar(value="safe")
        self.input_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Готово. Это визуальная песочница без микрофона и без обязательных моделей.")

        self._build_ui()
        self._append_log("Jarvis Sandbox запущен")
        self._append_log("Подсказка: попробуй 'покажи файлы', 'текущая папка', 'дата и время', 'запусти notepad'")

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer)
        header.pack(fill=tk.X, pady=(0, 12))

        title = ttk.Label(header, text="JARVIS — визуальная песочница", font=("Segoe UI", 18, "bold"))
        title.pack(side=tk.LEFT)

        badge = ttk.Label(header, text="offline preview", font=("Segoe UI", 10))
        badge.pack(side=tk.RIGHT, padx=(8, 0))

        top = ttk.Frame(outer)
        top.pack(fill=tk.X, pady=(0, 10))

        left = ttk.LabelFrame(top, text="Быстрые действия", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        quick_buttons = [
            ("Показать файлы", "покажи файлы"),
            ("Текущая папка", "текущая папка"),
            ("Дата и время", "дата и время"),
            ("Открыть блокнот", "запусти notepad"),
            ("Что ты умеешь", "что умеешь"),
        ]

        for idx, (label, command_text) in enumerate(quick_buttons):
            btn = ttk.Button(left, text=label, command=lambda text=command_text: self._run_input(text))
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)

        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=1)

        right = ttk.LabelFrame(top, text="Режим", padding=10)
        right.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Radiobutton(right, text="Safe preview", value="safe", variable=self.mode_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(right, text="Реальное выполнение", value="real", variable=self.mode_var).pack(anchor="w", pady=2)
        ttk.Label(
            right,
            text="Safe preview не запускает команды,\nа только показывает как Jarvis думает.",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(8, 0))

        middle = ttk.LabelFrame(outer, text="Ввод команды", padding=10)
        middle.pack(fill=tk.X, pady=(0, 10))

        entry = ttk.Entry(middle, textvariable=self.input_var, font=("Segoe UI", 11))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda _e: self._run_input())
        entry.focus_set()

        ttk.Button(middle, text="Отправить", command=self._run_input).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(middle, text="Очистить лог", command=self._clear_log).pack(side=tk.LEFT)

        panels = ttk.Panedwindow(outer, orient=tk.VERTICAL)
        panels.pack(fill=tk.BOTH, expand=True)

        top_panel = ttk.LabelFrame(panels, text="Лог Jarvis", padding=8)
        bottom_panel = ttk.LabelFrame(panels, text="Разбор запроса", padding=8)
        panels.add(top_panel, weight=3)
        panels.add(bottom_panel, weight=2)

        self.log = scrolledtext.ScrolledText(top_panel, wrap=tk.WORD, font=("Consolas", 10), height=18)
        self.log.pack(fill=tk.BOTH, expand=True)

        self.details = scrolledtext.ScrolledText(bottom_panel, wrap=tk.WORD, font=("Consolas", 10), height=10)
        self.details.pack(fill=tk.BOTH, expand=True)

        status = ttk.Label(outer, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status.pack(fill=tk.X, pady=(10, 0))

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _append_log(self, text: str) -> None:
        self.log.insert(tk.END, f"[{self._timestamp()}] {text}\n")
        self.log.see(tk.END)

    def _set_details(self, text: str) -> None:
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, text)

    def _clear_log(self) -> None:
        self.log.delete("1.0", tk.END)
        self.details.delete("1.0", tk.END)
        self.status_var.set("Лог очищен")

    def _run_input(self, forced_text: str | None = None) -> None:
        text = forced_text if forced_text is not None else self.input_var.get().strip()
        if not text:
            messagebox.showinfo("Jarvis Sandbox", "Введи команду или выбери быстрое действие.")
            return

        if forced_text is None:
            self.input_var.set("")

        self._append_log(f"Ты: {text}")

        try:
            plan = plan_command(text)
        except Exception as exc:
            self._append_log(f"Ошибка планирования: {exc}")
            self.status_var.set("Ошибка планирования")
            return

        decision_text = "нет команды"
        if plan.command:
            decision = check_command(plan.command)
            decision_text = (
                f"allowed={decision.allowed}, confirm={decision.requires_confirmation}, reason={decision.reason}"
            )
        else:
            decision = None

        details = [
            f"Запрос: {text}",
            f"Источник плана: {plan.source}",
            f"Intent: {plan.intent}",
            f"Reason: {plan.reason}",
            f"Command: {plan.command or '-'}",
            f"Safety: {decision_text}",
            f"Mode: {self.mode_var.get()}",
        ]
        self._set_details("\n".join(details))

        self._append_log(f"Jarvis: {plan.reason}")

        if plan.intent == "answer" or not plan.command:
            self.status_var.set("Ответ сформирован")
            return

        if decision and not decision.allowed:
            self._append_log("⛔ Команда заблокирована политикой безопасности")
            self.status_var.set("Команда заблокирована")
            return

        if self.mode_var.get() == "safe":
            self._append_log(f"[preview] Команда была бы выполнена: {plan.command}")
            self.status_var.set("Safe preview: только показ плана")
            return

        if decision and decision.requires_confirmation:
            ok = messagebox.askyesno("Подтверждение", f"Команда рискованная:\n\n{plan.command}\n\nВыполнить?")
            if not ok:
                self._append_log("Jarvis: Выполнение отменено пользователем")
                self.status_var.set("Отменено")
                return

        self._append_log(f"⚙ Выполняю: {plan.command}")
        result = run_command(plan.command)

        if result.stdout:
            self._append_log("STDOUT:")
            self._append_log(result.stdout)
        if result.stderr:
            self._append_log("STDERR:")
            self._append_log(result.stderr)

        self._append_log(f"Exit code: {result.exit_code}")
        self.status_var.set(f"Команда завершена с кодом {result.exit_code}")


def main() -> None:
    root = tk.Tk()
    try:
        from tkinter import TclError
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    app = JarvisSandboxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
