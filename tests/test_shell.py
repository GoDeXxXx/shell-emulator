"""Тесты разбора и выполнения команд."""

import unittest

from shell import Shell, ShellError, parse


class ParseTest(unittest.TestCase):
    """Тесты парсера командной строки."""

    def test_command_and_args(self):
        """Команда отделяется от аргументов."""
        self.assertEqual(parse("ls -l /home"), ("ls", ["-l", "/home"]))

    def test_extra_spaces(self):
        """Лишние пробелы игнорируются."""
        self.assertEqual(parse("  cd    docs  "), ("cd", ["docs"]))

    def test_empty_line(self):
        """Пустая строка не содержит команды."""
        self.assertEqual(parse("   "), (None, []))


class ShellTest(unittest.TestCase):
    """Тесты выполнения команд."""

    def setUp(self):
        """Создает новую оболочку для каждого теста."""
        self.shell = Shell()

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(self.shell.execute(""), "")

    def test_unknown_command(self):
        """Неизвестная команда вызывает ошибку."""
        with self.assertRaises(ShellError) as error:
            self.shell.execute("foo bar")
        self.assertEqual(str(error.exception), "foo: command not found")

    def test_ls_stub(self):
        """Заглушка ls выводит имя и аргументы."""
        self.assertEqual(self.shell.execute("ls -l /tmp"), "ls -l /tmp")

    def test_cd_stub(self):
        """Заглушка cd выводит имя и аргументы."""
        self.assertEqual(self.shell.execute("cd docs"), "cd docs")

    def test_cd_too_many_args(self):
        """Команда cd принимает не больше одного аргумента."""
        with self.assertRaises(ShellError):
            self.shell.execute("cd a b")

    def test_exit(self):
        """Команда exit останавливает оболочку."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)
        self.assertEqual(self.shell.exit_code, 0)

    def test_exit_with_code(self):
        """Команда exit сохраняет код завершения."""
        self.shell.execute("exit 3")
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_bad_code(self):
        """Код завершения должен быть числом."""
        with self.assertRaises(ShellError):
            self.shell.execute("exit abc")
        self.assertTrue(self.shell.running)

    def test_conf_dump(self):
        """Команда conf-dump выводит параметры запуска."""
        shell = Shell("vfs/test.xml", "start.txt")
        self.assertEqual(shell.execute("conf-dump"),
                         "vfs=vfs/test.xml\nscript=start.txt")

    def test_conf_dump_empty(self):
        """Незаданные параметры выводятся пустыми."""
        self.assertEqual(self.shell.execute("conf-dump"), "vfs=\nscript=")

    def test_conf_dump_args(self):
        """Команда conf-dump не принимает аргументы."""
        with self.assertRaises(ShellError):
            self.shell.execute("conf-dump -a")


if __name__ == "__main__":
    unittest.main()
