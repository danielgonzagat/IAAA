#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost:8000/health}"
MAX_TRIES="${2:-60}"
SLEEP="${3:-0.25}"
for ((i=1;i<=MAX_TRIES;i++)); do
  if curl -fsS "$URL" >/dev/null; then
    echo "ready: $URL"
    exit 0
  fi
  sleep "$SLEEP"
done
echo "timeout waiting for $URL"
exit 1
