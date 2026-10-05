"""Виртуальная файловая система, загружаемая из XML-файла."""

import base64
import binascii
import hashlib
import os
import re
from xml.etree.ElementTree import ParseError, fromstring

DIR_MODE = 0o755
FILE_MODE = 0o644


class VfsError(Exception):
    """Ошибка загрузки VFS."""


class Node:
    """Файл или каталог виртуальной файловой системы."""

    def __init__(self, name, is_dir, mode, data=b""):
        """Создает узел с заданным именем и правами доступа."""
        self.name = name
        self.is_dir = is_dir
        self.mode = mode
        self.data = data
        self.children = {}
        self.parent = None

    def add(self, node):
        """Добавляет дочерний узел в каталог."""
        node.parent = self
        self.children[node.name] = node


class Vfs:
    """Виртуальная файловая система, которая хранится в памяти."""

    def __init__(self, name="empty", root=None, digest=None):
        """Создает VFS, по умолчанию пустую."""
        self.name = name
        self.root = root or Node("", True, DIR_MODE)
        self.sha256 = digest or hashlib.sha256(b"").hexdigest()

    def find(self, cwd, path):
        """Возвращает узел по пути или None, если его нет."""
        node = self.root if path.startswith("/") else cwd
        for part in path.split("/"):
            node = step(node, part)
            if node is None:
                return None
        return node

    def path(self, node):
        """Возвращает абсолютный путь к узлу."""
        names = []
        while node is not self.root:
            names.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(names))


def step(node, part):
    """Делает один шаг по пути от узла node."""
    if part in ("", "."):
        return node
    if part == "..":
        return node.parent or node
    if not node.is_dir:
        return None
    return node.children.get(part)


def read_mode(element, default):
    """Читает права доступа из атрибута mode."""
    mode = element.get("mode")
    if mode is None:
        return default
    if not re.fullmatch("[0-7]{3}", mode):
        raise VfsError(f"vfs: invalid format: bad mode '{mode}'")
    return int(mode, 8)


def read_data(element):
    """Возвращает содержимое файла в виде байтов."""
    text = element.text or ""
    if element.get("encoding") != "base64":
        return text.encode("utf-8")
    try:
        return base64.b64decode("".join(text.split()), validate=True)
    except binascii.Error as error:
        name = element.get("name")
        message = f"vfs: invalid format: bad base64 in '{name}'"
        raise VfsError(message) from error


def build_node(element):
    """Создает узел VFS из XML-элемента."""
    if element.tag not in ("dir", "file"):
        raise VfsError(f"vfs: invalid format: unknown tag <{element.tag}>")
    name = element.get("name", "")
    if not name or "/" in name or name in (".", ".."):
        raise VfsError(f"vfs: invalid format: bad name '{name}'")
    if element.tag == "file":
        mode = read_mode(element, FILE_MODE)
        return Node(name, False, mode, read_data(element))
    node = Node(name, True, read_mode(element, DIR_MODE))
    for child in element:
        node.add(build_node(child))
    return node


def load_vfs(path):
    """Загружает VFS из XML-файла."""
    try:
        with open(path, "rb") as file:
            data = file.read()
    except FileNotFoundError as error:
        raise VfsError(f"vfs: file not found: {path}") from error
    except OSError as error:
        raise VfsError(f"vfs: cannot read file: {path}") from error
    try:
        element = fromstring(data)
    except ParseError as error:
        raise VfsError(f"vfs: invalid format: {error}") from error
    if element.tag != "vfs":
        raise VfsError("vfs: invalid format: root tag must be <vfs>")
    root = Node("", True, read_mode(element, DIR_MODE))
    for child in element:
        root.add(build_node(child))
    name = element.get("name", os.path.basename(path))
    return Vfs(name, root, hashlib.sha256(data).hexdigest())
