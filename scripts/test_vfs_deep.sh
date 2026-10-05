#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== VFS deep.xml без стартового скрипта"
python3 src/main.py --vfs vfs/deep.xml

echo "== VFS deep.xml со стартовым скриптом"
python3 src/main.py --vfs vfs/deep.xml --script startup/stage3.txt
