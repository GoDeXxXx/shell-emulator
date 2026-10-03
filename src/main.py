"""Запуск эмулятора командной строки."""

import argparse
import sys

from gui import ShellWindow
from shell import Shell


def parse_args():
    """Разбирает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument("--vfs", default="",
                        help="путь к физическому расположению VFS")
    parser.add_argument("--script", default="",
                        help="путь к стартовому скрипту")
    return parser.parse_args()


def main():
    """Создает оболочку и открывает окно эмулятора."""
    args = parse_args()
    shell = Shell(args.vfs, args.script)
    print("Параметры запуска:")
    print(shell.execute("conf-dump"))
    window = ShellWindow(shell)
    window.run()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
