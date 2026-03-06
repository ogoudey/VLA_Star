#!/usr/bin/env bash

echo "Opening list of asleep VLA*s"
FILE="$HOME/.vlastars.json"

if ! command -v jq >/dev/null; then
    echo "jq is required but not installed."
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "No ~/.vlastars.json file found."
    exit 1
fi

mapfile -t STARS < <(jq -r '.[]' "$FILE")

if [ ${#STARS[@]} -eq 0 ]; then
    echo "No stars found."
    exit 1
fi

echo "Select a VLA star:"
for i in "${!STARS[@]}"; do
    printf "%d) %s\n" "$((i+1))" "${STARS[$i]}"
done

while true; do
    read -rp "$STARS Enter index: " CHOICE

    if [[ "$CHOICE" =~ ^[0-9]+$ ]] && (( CHOICE>=1 && CHOICE<=${#STARS[@]} )); then
        echo "${STARS[$((CHOICE-1))]}"
        exit 0
    fi

    echo "Invalid selection."
done