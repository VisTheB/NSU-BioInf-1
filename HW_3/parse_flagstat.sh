#!/bin/bash

# Использование:
#   ./parse_flagstat.sh sample.flagstat.txt

FILE="$1"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    echo "Использование: $0 <файл_с_выводом_flagstat>" >&2
    exit 1
fi

PCT=$(awk '/ mapped \(/ && !/primary/ && !/properly/ {print}' "$FILE" \
        | grep -oE '[0-9]+\.[0-9]+' \
        | head -n 1)

if [ -z "$PCT" ]; then
    echo "Не удалось найти процент картированных ридов в файле $FILE" >&2
    exit 1
fi

echo "$PCT"
