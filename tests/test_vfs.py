"""Тесты загрузки виртуальной файловой системы."""

import hashlib
import os
import tempfile
import unittest

from shell import Shell
from vfs import VfsError, load_vfs

VFS_DIR = os.path.join(os.path.dirname(__file__), "..", "vfs")


def sample(name):
    """Возвращает путь к примеру VFS из папки vfs."""
    return os.path.join(VFS_DIR, name)


class LoadVfsTest(unittest.TestCase):
    """Тесты функции load_vfs на готовых примерах."""

    def test_minimal(self):
        """Минимальная VFS содержит один файл."""
        vfs = load_vfs(sample("minimal.xml"))
        self.assertEqual(vfs.name, "minimal")
        self.assertEqual(list(vfs.root.children), ["hello.txt"])
        node = vfs.find(vfs.root, "hello.txt")
        self.assertEqual(node.data, b"Hello, world!")

    def test_sha256(self):
        """Хеш считается по данным XML-файла."""
        with open(sample("minimal.xml"), "rb") as file:
            expected = hashlib.sha256(file.read()).hexdigest()
        self.assertEqual(load_vfs(sample("minimal.xml")).sha256, expected)

    def test_base64(self):
        """Двоичные данные декодируются из base64."""
        vfs = load_vfs(sample("files.xml"))
        node = vfs.find(vfs.root, "/data.bin")
        self.assertEqual(node.data, bytes(range(10)))
        self.assertTrue(vfs.find(vfs.root, "pixel.png").data.startswith(
            b"\x89PNG"))

    def test_mode(self):
        """Права доступа читаются из атрибута mode."""
        vfs = load_vfs(sample("files.xml"))
        self.assertEqual(vfs.find(vfs.root, "run.sh").mode, 0o755)
        self.assertEqual(vfs.find(vfs.root, "readme.txt").mode, 0o644)

    def test_deep(self):
        """Вложенность каталогов сохраняется."""
        vfs = load_vfs(sample("deep.xml"))
        node = vfs.find(vfs.root, "/home/user/docs/old/todo.txt")
        self.assertIsNotNone(node)
        self.assertFalse(node.is_dir)
        self.assertEqual(vfs.path(node), "/home/user/docs/old/todo.txt")

    def test_relative_path(self):
        """Относительные пути и .. работают от текущего каталога."""
        vfs = load_vfs(sample("deep.xml"))
        docs = vfs.find(vfs.root, "/home/user/docs")
        self.assertIs(vfs.find(docs, "../../.."), vfs.root)
        self.assertIs(vfs.find(docs, "old/../notes.txt"),
                      docs.children["notes.txt"])
        self.assertIsNone(vfs.find(docs, "missing"))

    def test_file_not_found(self):
        """Ошибка, если файл VFS не найден."""
        with self.assertRaises(VfsError) as error:
            load_vfs(sample("missing.xml"))
        self.assertIn("file not found", str(error.exception))

    def test_broken_xml(self):
        """Ошибка, если XML некорректный."""
        with self.assertRaises(VfsError) as error:
            load_vfs(sample("broken.xml"))
        self.assertIn("invalid format", str(error.exception))


class BadFormatTest(unittest.TestCase):
    """Тесты ошибок формата во временных файлах."""

    def load(self, text):
        """Сохраняет текст во временный файл и загружает его как VFS."""
        handle, path = tempfile.mkstemp(suffix=".xml")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(text)
        try:
            return load_vfs(path)
        finally:
            os.remove(path)

    def test_wrong_root(self):
        """Корневой элемент должен называться vfs."""
        with self.assertRaises(VfsError):
            self.load("<root><file name='a'/></root>")

    def test_unknown_tag(self):
        """Неизвестный элемент внутри VFS."""
        with self.assertRaises(VfsError):
            self.load("<vfs><link name='a'/></vfs>")

    def test_bad_name(self):
        """Имя файла не может быть пустым или содержать /."""
        with self.assertRaises(VfsError):
            self.load("<vfs><file name='a/b'/></vfs>")
        with self.assertRaises(VfsError):
            self.load("<vfs><dir/></vfs>")

    def test_bad_mode(self):
        """Права доступа задаются тремя восьмеричными цифрами."""
        with self.assertRaises(VfsError):
            self.load("<vfs><file name='a' mode='999'/></vfs>")

    def test_bad_base64(self):
        """Некорректные данные base64."""
        with self.assertRaises(VfsError):
            self.load("<vfs><file name='a' encoding='base64'>@@</file></vfs>")


class VfsInfoTest(unittest.TestCase):
    """Тесты команды vfs-info."""

    def test_loaded(self):
        """Выводятся имя и хеш загруженной VFS."""
        shell = Shell(sample("deep.xml"))
        shell.load_vfs()
        lines = shell.execute("vfs-info").splitlines()
        self.assertEqual(lines[0], "name: deep")
        self.assertEqual(lines[1], "sha256: " + shell.vfs.sha256)

    def test_empty(self):
        """Без параметра --vfs используется пустая VFS."""
        shell = Shell()
        shell.load_vfs()
        self.assertIn("name: empty", shell.execute("vfs-info"))


if __name__ == "__main__":
    unittest.main()
