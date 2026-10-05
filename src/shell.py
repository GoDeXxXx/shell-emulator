"""Логика эмулятора: разбор и выполнение команд."""

import getpass
import socket

from vfs import Vfs, load_vfs


class ShellError(Exception):
    """Ошибка при выполнении команды."""


def parse(line):
    """Разбивает строку на имя команды и список аргументов."""
    parts = line.split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def read_script(path):
    """Читает стартовый скрипт и возвращает список команд."""
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ShellError(f"script: cannot read file '{path}'") from error
    return [line for line in lines
            if line.strip() and not line.lstrip().startswith("#")]


class Shell:
    """Эмулятор командной оболочки UNIX."""

    def __init__(self, vfs_path="", script_path=""):
        """Создает оболочку с заданными параметрами запуска."""
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.config = {"vfs": vfs_path, "script": script_path}
        self.vfs = Vfs()
        self.cwd = self.vfs.root
        self.running = True
        self.exit_code = 0
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
            "conf-dump": self.cmd_conf_dump,
            "vfs-info": self.cmd_vfs_info,
        }

    def load_vfs(self):
        """Загружает VFS по пути из параметров запуска."""
        if self.config["vfs"]:
            self.vfs = load_vfs(self.config["vfs"])
            self.cwd = self.vfs.root

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

    def cmd_conf_dump(self, args):
        """Выводит параметры эмулятора в формате ключ=значение."""
        if args:
            raise ShellError("conf-dump: too many arguments")
        lines = [f"{key}={value}" for key, value in self.config.items()]
        return "\n".join(lines)

    def cmd_vfs_info(self, args):
        """Выводит имя загруженной VFS и SHA-256 ее данных."""
        if args:
            raise ShellError("vfs-info: too many arguments")
        return f"name: {self.vfs.name}\nsha256: {self.vfs.sha256}"
