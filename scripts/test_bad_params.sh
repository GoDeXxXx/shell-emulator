#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== несуществующий стартовый скрипт"
python3 src/main.py --vfs vfs/minimal.xml --script startup/missing.txt

echo "== неизвестный параметр"
python3 src/main.py --vfs vfs/minimal.xml --config test.ini

echo "== параметр без значения"
python3 src/main.py --script
