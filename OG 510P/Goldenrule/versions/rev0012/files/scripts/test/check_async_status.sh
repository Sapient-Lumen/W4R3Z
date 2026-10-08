#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${1:-artifacts/timing/soak_async.pid}"
LOG_FILE="${2:-artifacts/timing/soak_async.log}"

if [[ ! -f "$PID_FILE" ]]; then
  echo "async: no pid file at $PID_FILE"
  exit 0
fi

pid="$(cat "$PID_FILE")"
if [[ -z "$pid" ]]; then
  echo "async: pid file is empty ($PID_FILE)"
  exit 1
fi

if kill -0 "$pid" >/dev/null 2>&1; then
  echo "async: running pid=$pid"
  [[ -f "$LOG_FILE" ]] && tail -n 20 "$LOG_FILE" || true
  exit 0
fi

echo "async: finished pid=$pid"
[[ -f "$LOG_FILE" ]] && tail -n 40 "$LOG_FILE" || true
exit 0
