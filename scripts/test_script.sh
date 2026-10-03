#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== стартовый скрипт с относительным путем"
python3 src/main.py --vfs vfs/minimal.xml --script startup/stage2.txt

echo "== стартовый скрипт с абсолютным путем"
python3 src/main.py --vfs "$(pwd)/vfs/minimal.xml" \
    --script "$(pwd)/startup/stage2.txt"
