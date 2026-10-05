#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== VFS files.xml без стартового скрипта"
python3 src/main.py --vfs vfs/files.xml

echo "== VFS files.xml со стартовым скриптом"
python3 src/main.py --vfs vfs/files.xml --script startup/stage3.txt
