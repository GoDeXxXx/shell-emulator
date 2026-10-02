"""Запуск эмулятора командной строки."""

import sys

from gui import ShellWindow
from shell import Shell


def main():
    """Создает оболочку и открывает окно эмулятора."""
    shell = Shell()
    window = ShellWindow(shell)
    window.run()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
