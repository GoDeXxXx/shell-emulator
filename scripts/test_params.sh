#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== без параметров"
python3 src/main.py

echo "== только --vfs"
python3 src/main.py --vfs vfs/minimal.xml

echo "== только --script"
python3 src/main.py --script startup/stage2.txt

echo "== --vfs и --script"
python3 src/main.py --vfs vfs/minimal.xml --script startup/stage2.txt
