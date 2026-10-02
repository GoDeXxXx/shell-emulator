"""Логика эмулятора: разбор и выполнение команд."""

import getpass
import socket


class ShellError(Exception):
    """Ошибка при выполнении команды."""


def parse(line):
    """Разбивает строку на имя команды и список аргументов."""
    parts = line.split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


class Shell:
    """Эмулятор командной оболочки UNIX."""

    def __init__(self):
        """Создает оболочку для текущего пользователя."""
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.running = True
        self.exit_code = 0
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def prompt(self):
        """Возвращает приглашение командной строки."""
        return f"{self.user}@{self.host}:~$ "

    def execute(self, line):
        """Выполняет строку и возвращает вывод команды."""
        name, args = parse(line)
        if name is None:
            return ""
        if name not in self.commands:
            raise ShellError(f"{name}: command not found")
        return self.commands[name](args)

    def cmd_ls(self, args):
        """Заглушка команды ls: выводит имя и аргументы."""
        return " ".join(["ls"] + args)

    def cmd_cd(self, args):
        """Заглушка команды cd: выводит имя и аргументы."""
        if args[1:]:
            raise ShellError("cd: too many arguments")
        return " ".join(["cd"] + args)

    def cmd_exit(self, args):
        """Завершает работу эмулятора с указанным кодом."""
        if args[1:]:
            raise ShellError("exit: too many arguments")
        if args and not args[0].isdigit():
            raise ShellError(f"exit: {args[0]}: numeric argument required")
        self.exit_code = int(args[0]) if args else 0
        self.running = False
        return ""
