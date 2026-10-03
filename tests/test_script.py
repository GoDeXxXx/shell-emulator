"""Тесты чтения стартового скрипта."""

import os
import tempfile
import unittest

from shell import ShellError, read_script


class ReadScriptTest(unittest.TestCase):
    """Тесты функции read_script."""

    def setUp(self):
        """Создает временный файл скрипта."""
        handle, self.path = tempfile.mkstemp(suffix=".txt")
        os.close(handle)

    def tearDown(self):
        """Удаляет временный файл."""
        os.remove(self.path)

    def write(self, text):
        """Записывает текст во временный файл."""
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(text)

    def test_commands(self):
        """Команды читаются построчно."""
        self.write("ls\ncd docs\n")
        self.assertEqual(read_script(self.path), ["ls", "cd docs"])

    def test_skip_comments_and_empty(self):
        """Комментарии и пустые строки пропускаются."""
        self.write("# comment\n\nls\n   \n")
        self.assertEqual(read_script(self.path), ["ls"])

    def test_missing_file(self):
        """Отсутствующий файл вызывает ошибку."""
        with self.assertRaises(ShellError):
            read_script(self.path + ".missing")


if __name__ == "__main__":
    unittest.main()
