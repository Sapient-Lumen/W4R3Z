#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="$ROOT/artifacts/process"
mkdir -p "$STATE_DIR"

usage() {
  cat <<USAGE
usage: scripts/procctl.sh <command> [args]
commands:
  start <name> -- <cmd...>
  list
  status <name>
  stop <name>
  stop-all
  logs <name>
  prune
  hygiene
USAGE
}

pid_file_for() {
  printf "%s/%s.pid" "$STATE_DIR" "$1"
}

log_file_for() {
  printf "%s/%s.log" "$STATE_DIR" "$1"
}

cmd_file_for() {
  printf "%s/%s.cmd" "$STATE_DIR" "$1"
}

require_name() {
  if [[ -z "${1:-}" ]]; then
    echo "procctl: missing process name" >&2
    exit 2
  fi
}

is_running() {
  local pid="$1"
  kill -0 "$pid" >/dev/null 2>&1
}

start_proc() {
  local name="$1"
  shift

  require_name "$name"

  if [[ "${1:-}" != "--" ]]; then
    echo "procctl: expected '--' before command" >&2
    exit 2
  fi
  shift
  if [[ $# -eq 0 ]]; then
    echo "procctl: missing command" >&2
    exit 2
  fi

  local pid_file log_file cmd_file
  pid_file="$(pid_file_for "$name")"
  log_file="$(log_file_for "$name")"
  cmd_file="$(cmd_file_for "$name")"

  if [[ -f "$pid_file" ]]; then
    local existing_pid
    existing_pid="$(cat "$pid_file")"
    if [[ -n "$existing_pid" ]] && is_running "$existing_pid"; then
      echo "procctl: '$name' already running pid=$existing_pid"
      exit 1
    fi
    rm -f "$pid_file"
  fi

  {
    printf '%q ' "$@"
    printf '\n'
  } >"$cmd_file"

  nohup bash -lc "cd '$ROOT' && $*" >"$log_file" 2>&1 &
  local pid=$!
  echo "$pid" >"$pid_file"
  echo "procctl: started '$name' pid=$pid log=$log_file"
}

list_proc() {
  local found=0
  for pf in "$STATE_DIR"/*.pid; do
    [[ -e "$pf" ]] || continue
    found=1
    local name pid state
    name="$(basename "$pf" .pid)"
    pid="$(cat "$pf")"
    if [[ -n "$pid" ]] && is_running "$pid"; then
      state="running"
    else
      state="stale"
    fi
    echo "$name pid=$pid state=$state"
  done
  if [[ "$found" -eq 0 ]]; then
    echo "procctl: no managed processes"
  fi
}

status_proc() {
  local name="$1"
  require_name "$name"

  local pid_file log_file cmd_file
  pid_file="$(pid_file_for "$name")"
  log_file="$(log_file_for "$name")"
  cmd_file="$(cmd_file_for "$name")"

  if [[ ! -f "$pid_file" ]]; then
    echo "procctl: '$name' not found"
    exit 1
  fi

  local pid
  pid="$(cat "$pid_file")"
  echo "name=$name"
  echo "pid=$pid"
  echo "cmd=$(cat "$cmd_file" 2>/dev/null || true)"
  echo "log=$log_file"

  if [[ -n "$pid" ]] && is_running "$pid"; then
    echo "state=running"
    exit 0
  fi

  echo "state=stale"
  exit 1
}

stop_proc() {
  local name="$1"
  require_name "$name"

  local pid_file
  pid_file="$(pid_file_for "$name")"

  if [[ ! -f "$pid_file" ]]; then
    echo "procctl: '$name' not found"
    exit 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -n "$pid" ]] && is_running "$pid"; then
    kill "$pid" >/dev/null 2>&1 || true
    sleep 1
    if is_running "$pid"; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    echo "procctl: stopped '$name' pid=$pid"
  else
    echo "procctl: '$name' already stopped"
  fi

  rm -f "$pid_file"
}

stop_all() {
  local pf
  for pf in "$STATE_DIR"/*.pid; do
    [[ -e "$pf" ]] || continue
    local name
    name="$(basename "$pf" .pid)"
    stop_proc "$name" || true
  done
}

logs_proc() {
  local name="$1"
  require_name "$name"
  local log_file
  log_file="$(log_file_for "$name")"
  if [[ ! -f "$log_file" ]]; then
    echo "procctl: no log for '$name'"
    exit 1
  fi
  tail -n 80 "$log_file"
}

prune_proc() {
  local pf
  for pf in "$STATE_DIR"/*.pid; do
    [[ -e "$pf" ]] || continue
    local name pid
    name="$(basename "$pf" .pid)"
    pid="$(cat "$pf")"
    if [[ -z "$pid" ]] || ! is_running "$pid"; then
      rm -f "$pf"
      echo "procctl: pruned stale pid for '$name'"
    fi
  done
}

hygiene() {
  local leaked=0
  local pf
  for pf in "$STATE_DIR"/*.pid; do
    [[ -e "$pf" ]] || continue
    local name pid
    name="$(basename "$pf" .pid)"
    pid="$(cat "$pf")"
    if [[ -n "$pid" ]] && is_running "$pid"; then
      echo "hygiene: leaked managed process '$name' pid=$pid"
      leaked=1
    elif [[ -f "$pf" ]]; then
      echo "hygiene: stale pid file for '$name' (run scripts/procctl.sh prune)"
      leaked=1
    fi
  done

  # Data-store leakage guardrail for local sqlite artifacts.
  if find "$ROOT/artifacts" -type f -name '*.sqlite*' 2>/dev/null | grep -q .; then
    echo "hygiene: sqlite artifacts found under artifacts/ (clean before deterministic runs)"
    leaked=1
  fi

  if [[ "$leaked" -ne 0 ]]; then
    exit 1
  fi

  echo "hygiene: ok"
}

cmd="${1:-}"
shift || true

case "$cmd" in
  start)
    start_proc "$@"
    ;;
  list)
    list_proc
    ;;
  status)
    status_proc "$@"
    ;;
  stop)
    stop_proc "$@"
    ;;
  stop-all)
    stop_all
    ;;
  logs)
    logs_proc "$@"
    ;;
  prune)
    prune_proc
    ;;
  hygiene)
    hygiene
    ;;
  *)
    usage
    exit 2
    ;;
esac
