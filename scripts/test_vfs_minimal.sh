#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== VFS minimal.xml без стартового скрипта"
python3 src/main.py --vfs vfs/minimal.xml

echo "== VFS minimal.xml со стартовым скриптом"
python3 src/main.py --vfs vfs/minimal.xml --script startup/stage3.txt
