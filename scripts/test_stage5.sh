#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== команды этапа 5 на VFS deep.xml"
python3 src/main.py --vfs vfs/deep.xml --script startup/stage5.txt

echo "== команды этапа 5 на пустой VFS"
python3 src/main.py --script startup/stage5.txt
