"""Логика эмулятора: разбор и выполнение команд."""

import getpass
import math
import platform
import socket
import time

from vfs import Vfs, load_vfs

DATE_FORMAT = "%a %b %d %H:%M:%S %Z %Y"
UNAME_FLAGS = "snrvm"
KILOBYTE = 1024
SIZE_UNITS = "KMGT"
SMALL_SIZE = 10


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


def split_options(name, args, allowed):
    """Отделяет короткие опции вида -l от остальных аргументов."""
    flags = set()
    operands = []
    for arg in args:
        if not arg.startswith("-"):
            operands.append(arg)
            continue
        for flag in arg[1:]:
            if flag not in allowed:
                raise ShellError(f"{name}: invalid option -- '{flag}'")
            flags.add(flag)
    return flags, operands


def human_size(size):
    """Возвращает размер в читаемом виде: 512, 1.5K, 20M."""
    if size < KILOBYTE:
        return str(size)
    value = size / KILOBYTE
    index = 0
    while value >= KILOBYTE and index < len(SIZE_UNITS) - 1:
        value /= KILOBYTE
        index += 1
    unit = SIZE_UNITS[index]
    if value < SMALL_SIZE:
        value = math.ceil(value * SMALL_SIZE) / SMALL_SIZE
        if value < SMALL_SIZE:
            return f"{value:.1f}{unit}"
    return f"{math.ceil(value)}{unit}"


def list_dir(node, show_all):
    """Возвращает пары (имя, узел) для содержимого каталога."""
    entries = sorted(node.children.items())
    if show_all:
        return [(".", node), ("..", node.parent or node)] + entries
    return [(name, item) for name, item in entries
            if not name.startswith(".")]


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
            "date": self.cmd_date,
            "tac": self.cmd_tac,
            "uname": self.cmd_uname,
        }

    def load_vfs(self):
        """Загружает VFS по пути из параметров запуска."""
        if self.config["vfs"]:
            self.vfs = load_vfs(self.config["vfs"])
            self.cwd = self.vfs.root

    def prompt(self):
        """Возвращает приглашение командной строки."""
        path = self.vfs.path(self.cwd)
        return f"{self.user}@{self.host}:{path}$ "

    def execute(self, line):
        """Выполняет строку и возвращает вывод команды."""
        name, args = parse(line)
        if name is None:
            return ""
        if name not in self.commands:
            raise ShellError(f"{name}: command not found")
        return self.commands[name](args)

    def find(self, name, path):
        """Ищет узел по пути, если его нет, сообщает об ошибке."""
        node = self.vfs.find(self.cwd, path)
        if node is None:
            raise ShellError(f"{name}: {path}: No such file or directory")
        return node

    def long_entry(self, name, node, human):
        """Возвращает строку для подробного вывода ls -l."""
        size = len(node.data)
        if human:
            size = human_size(size)
        return f"{node.mode_string()} {self.user} {size:>6} {name}"

    def cmd_ls(self, args):
        """Выводит содержимое каталога или имя файла."""
        flags, paths = split_options("ls", args, "ahl")
        if paths[1:]:
            raise ShellError("ls: too many arguments")
        path = paths[0] if paths else "."
        node = self.find("ls", path)
        if node.is_dir:
            entries = list_dir(node, "a" in flags)
        else:
            entries = [(path, node)]
        if "l" in flags:
            human = "h" in flags
            lines = [self.long_entry(name, item, human)
                     for name, item in entries]
            return "\n".join(lines)
        return "  ".join(name for name, _ in entries)

    def cmd_cd(self, args):
        """Меняет текущий каталог, без аргументов переходит в корень."""
        if args[1:]:
            raise ShellError("cd: too many arguments")
        path = args[0] if args else "/"
        node = self.find("cd", path)
        if not node.is_dir:
            raise ShellError(f"cd: {path}: Not a directory")
        self.cwd = node
        return ""

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

    def cmd_date(self, args):
        """Выводит текущие дату и время, формат задается через +."""
        if args[1:]:
            raise ShellError(f"date: extra operand '{args[1]}'")
        if args and not args[0].startswith("+"):
            raise ShellError(f"date: invalid date '{args[0]}'")
        date_format = args[0][1:] if args else DATE_FORMAT
        return time.strftime(date_format)

    def cmd_tac(self, args):
        """Выводит строки файлов в обратном порядке."""
        if not args:
            raise ShellError("tac: missing file operand")
        result = []
        for path in args:
            node = self.find("tac", path)
            if node.is_dir:
                raise ShellError(f"tac: {path}: Is a directory")
            text = node.data.decode("utf-8", errors="replace")
            result.extend(reversed(text.splitlines()))
        return "\n".join(result)

    def cmd_uname(self, args):
        """Выводит информацию о системе."""
        flags, operands = split_options("uname", args, UNAME_FLAGS + "a")
        if operands:
            raise ShellError(f"uname: extra operand '{operands[0]}'")
        info = platform.uname()
        fields = [info.system, info.node, info.release, info.version,
                  info.machine]
        values = dict(zip(UNAME_FLAGS, fields))
        if "a" in flags:
            flags = set(UNAME_FLAGS)
        keys = [key for key in UNAME_FLAGS if key in flags] or ["s"]
        return " ".join(values[key] for key in keys)
