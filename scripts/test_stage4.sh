#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== команды этапа 4 на VFS deep.xml"
python3 src/main.py --vfs vfs/deep.xml --script startup/stage4.txt

echo "== команды этапа 4 на минимальной VFS"
python3 src/main.py --vfs vfs/minimal.xml --script startup/stage4.txt
