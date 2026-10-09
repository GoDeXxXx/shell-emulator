"""Тесты основных команд на примере VFS deep.xml."""

import os
import platform
import time
import unittest

from shell import Shell, ShellError, human_size

DEEP_VFS = os.path.join(os.path.dirname(__file__), "..", "vfs", "deep.xml")


class CommandTestCase(unittest.TestCase):
    """Базовый класс: оболочка с загруженной VFS."""

    def setUp(self):
        """Загружает VFS deep.xml."""
        self.shell = Shell(DEEP_VFS)
        self.shell.load_vfs()

    def run_cmd(self, line):
        """Выполняет команду и возвращает ее вывод."""
        return self.shell.execute(line)

    def assert_error(self, line, message):
        """Проверяет, что команда завершается с ошибкой."""
        with self.assertRaises(ShellError) as error:
            self.shell.execute(line)
        self.assertEqual(str(error.exception), message)


class LsTest(CommandTestCase):
    """Тесты команды ls."""

    def test_root(self):
        """Содержимое корня выводится по алфавиту."""
        self.assertEqual(self.run_cmd("ls"), "bin  etc  home  tmp")

    def test_hidden_files(self):
        """Скрытые файлы видны только с опцией -a."""
        self.assertEqual(self.run_cmd("ls /home/user"), "docs")
        self.assertEqual(self.run_cmd("ls -a /home/user"),
                         ".  ..  .profile  docs")

    def test_long_format(self):
        """Опция -l выводит права доступа и размер."""
        lines = self.run_cmd("ls -l /home/user/docs").splitlines()
        self.assertTrue(lines[0].startswith("-rw-r--r--"))
        self.assertTrue(lines[0].endswith("notes.txt"))
        self.assertTrue(lines[1].startswith("drwxr-xr-x"))

    def test_combined_options(self):
        """Опции можно объединять: -la."""
        self.assertEqual(self.run_cmd("ls -la /home/user"),
                         self.run_cmd("ls -a -l /home/user"))

    def test_file(self):
        """Для файла выводится его путь."""
        self.assertEqual(self.run_cmd("ls /etc/passwd"), "/etc/passwd")

    def test_human_size(self):
        """Опция -h вместе с -l выводит размер в читаемом виде."""
        self.assertTrue(self.run_cmd("ls -l /bin").endswith(" 2600 hello"))
        self.assertTrue(self.run_cmd("ls -lh /bin").endswith(" 2.6K hello"))
        self.assertEqual(self.run_cmd("ls -h /bin"), "hello")

    def test_errors(self):
        """Ошибки ls."""
        self.assert_error("ls /nope", "ls: /nope: No such file or directory")
        self.assert_error("ls -z", "ls: invalid option -- 'z'")
        self.assert_error("ls /etc /bin", "ls: too many arguments")


class HumanSizeTest(unittest.TestCase):
    """Тесты перевода размера в читаемый вид."""

    def test_bytes(self):
        """Размер меньше килобайта выводится в байтах."""
        self.assertEqual(human_size(0), "0")
        self.assertEqual(human_size(1023), "1023")

    def test_units(self):
        """Большие размеры выводятся в K, M и G."""
        self.assertEqual(human_size(1024), "1.0K")
        self.assertEqual(human_size(1536), "1.5K")
        self.assertEqual(human_size(10240), "10K")
        self.assertEqual(human_size(5 * 1024 * 1024), "5.0M")
        self.assertEqual(human_size(3 * 1024 ** 3), "3.0G")

    def test_round_up(self):
        """Дробная часть округляется вверх, как в ls."""
        self.assertEqual(human_size(2600), "2.6K")
        self.assertEqual(human_size(10239), "10K")


class CdTest(CommandTestCase):
    """Тесты команды cd."""

    def test_absolute_and_relative(self):
        """Переход по абсолютному и относительному пути."""
        self.run_cmd("cd /home")
        self.run_cmd("cd user/docs")
        self.assertEqual(self.run_cmd("ls"), "notes.txt  old")
        self.assertIn(":/home/user/docs$", self.shell.prompt())

    def test_parent(self):
        """Переход в родительский каталог."""
        self.run_cmd("cd /home/user/docs/old")
        self.run_cmd("cd ../..")
        self.assertIn(":/home/user$", self.shell.prompt())

    def test_root(self):
        """Без аргументов cd переходит в корень."""
        self.run_cmd("cd /etc")
        self.run_cmd("cd")
        self.assertIn(":/$", self.shell.prompt())

    def test_errors(self):
        """Ошибки cd не меняют текущий каталог."""
        self.assert_error("cd /nope", "cd: /nope: No such file or directory")
        self.assert_error("cd /etc/passwd", "cd: /etc/passwd: Not a directory")
        self.assertIn(":/$", self.shell.prompt())


class DateTest(CommandTestCase):
    """Тесты команды date."""

    def test_default(self):
        """По умолчанию выводится год."""
        self.assertIn(time.strftime("%Y"), self.run_cmd("date"))

    def test_format(self):
        """Формат задается аргументом, начинающимся с +."""
        self.assertEqual(self.run_cmd("date +%Y"), time.strftime("%Y"))

    def test_errors(self):
        """Ошибки date."""
        self.assert_error("date now", "date: invalid date 'now'")
        self.assert_error("date +%Y +%m", "date: extra operand '+%m'")


class TacTest(CommandTestCase):
    """Тесты команды tac."""

    def test_one_file(self):
        """Строки файла выводятся в обратном порядке."""
        self.assertEqual(self.run_cmd("tac /home/user/docs/notes.txt"),
                         "third line\nsecond line\nfirst line")

    def test_two_files(self):
        """Файлы обрабатываются по очереди."""
        self.run_cmd("cd /home/user/docs")
        result = self.run_cmd("tac notes.txt old/todo.txt").splitlines()
        self.assertEqual(result[2], "first line")
        self.assertEqual(result[3], "pass the lab")

    def test_errors(self):
        """Ошибки tac."""
        self.assert_error("tac", "tac: missing file operand")
        self.assert_error("tac /etc", "tac: /etc: Is a directory")
        self.assert_error("tac a.txt", "tac: a.txt: No such file or directory")


class UnameTest(CommandTestCase):
    """Тесты команды uname."""

    def test_default(self):
        """Без опций выводится имя системы."""
        self.assertEqual(self.run_cmd("uname"), platform.system())

    def test_options(self):
        """Опции -s и -m."""
        expected = f"{platform.system()} {platform.machine()}"
        self.assertEqual(self.run_cmd("uname -sm"), expected)

    def test_all(self):
        """Опция -a выводит все поля."""
        result = self.run_cmd("uname -a")
        self.assertTrue(result.startswith(platform.system()))
        self.assertTrue(result.endswith(platform.machine()))

    def test_errors(self):
        """Ошибки uname."""
        self.assert_error("uname -q", "uname: invalid option -- 'q'")
        self.assert_error("uname all", "uname: extra operand 'all'")


if __name__ == "__main__":
    unittest.main()
