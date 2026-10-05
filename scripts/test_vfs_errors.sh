#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== файл VFS не найден"
python3 src/main.py --vfs vfs/missing.xml --script startup/stage3.txt

echo "== неверный формат VFS"
python3 src/main.py --vfs vfs/broken.xml --script startup/stage3.txt

echo "== вместо XML передан текстовый файл"
python3 src/main.py --vfs README.md --script startup/stage3.txt
