#!/usr/bin/env bash

#!/bin/bash
echo "Opening list of asleep VLA*s" >&2
FILE="$HOME/.vla_stars.json"
if ! command -v jq >/dev/null; then
    echo "jq is required but not installed." >&2
    exit 1
fi
if [ ! -f "$FILE" ]; then
    echo "No ~/.vlastars.json file found." >&2
    exit 1
fi
mapfile -t STARS < <(jq -r '.[]' "$FILE")
if [ ${#STARS[@]} -eq 0 ]; then
    echo "No stars found." >&2
    exit 1
fi
printf '%s\n' "${STARS[@]}"
