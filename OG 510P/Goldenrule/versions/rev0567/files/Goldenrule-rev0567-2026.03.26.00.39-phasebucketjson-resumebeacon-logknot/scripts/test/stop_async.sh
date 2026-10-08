#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${1:-artifacts/timing/soak_async.pid}"

if [[ ! -f "$PID_FILE" ]]; then
  echo "async-stop: no pid file at $PID_FILE"
  exit 0
fi

pid="$(cat "$PID_FILE")"
if [[ -z "$pid" ]]; then
  rm -f "$PID_FILE"
  echo "async-stop: empty pid file removed"
  exit 0
fi

if kill -0 "$pid" >/dev/null 2>&1; then
  kill "$pid" >/dev/null 2>&1 || true
  sleep 1
  if kill -0 "$pid" >/dev/null 2>&1; then
    kill -9 "$pid" >/dev/null 2>&1 || true
  fi
  echo "async-stop: stopped pid=$pid"
else
  echo "async-stop: pid=$pid already exited"
fi

rm -f "$PID_FILE"
