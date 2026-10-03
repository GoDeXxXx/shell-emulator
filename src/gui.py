"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from shell import ShellError, read_script

FONT = ("Courier", 13)


class ShellWindow:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создает окно для переданной оболочки."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{shell.user}@{shell.host}]")
        self.output = scrolledtext.ScrolledText(
            self.root, width=90, height=25, font=FONT, state="disabled")
        self.output.pack(fill="both", expand=True)
        bottom = tk.Frame(self.root)
        bottom.pack(fill="x")
        self.prompt = tk.Label(bottom, text=shell.prompt(), font=FONT)
        self.prompt.pack(side="left")
        self.entry = tk.Entry(bottom, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()

    def write(self, text):
        """Добавляет текст в область вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def run_command(self, line):
        """Выполняет команду, возвращает False при ошибке или выходе."""
        self.write(self.shell.prompt() + line)
        try:
            result = self.shell.execute(line)
        except ShellError as error:
            self.write(str(error))
            return False
        if result:
            self.write(result)
        if not self.shell.running:
            self.root.destroy()
            return False
        self.prompt.configure(text=self.shell.prompt())
        return True

    def on_enter(self, _event):
        """Обрабатывает нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.run_command(line)

    def run_script(self, path):
        """Выполняет команды стартового скрипта до первой ошибки."""
        try:
            lines = read_script(path)
        except ShellError as error:
            self.write(str(error))
            return
        for line in lines:
            if self.run_command(line):
                continue
            if self.shell.running:
                self.write("Выполнение скрипта остановлено из-за ошибки")
            return

    def run(self):
        """Запускает стартовый скрипт и главный цикл окна."""
        if self.shell.config["script"]:
            self.root.after(100, self.run_script, self.shell.config["script"])
        self.root.mainloop()
