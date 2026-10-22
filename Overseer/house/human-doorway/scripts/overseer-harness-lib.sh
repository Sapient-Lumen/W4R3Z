#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "source this file from a harness entrypoint" >&2
  exit 1
fi

set -euo pipefail

OVERSEER_HOME="${OVERSEER_HOME:-/home/overseer}"
OVERSEER_ROOT="${OVERSEER_ROOT:-$OVERSEER_HOME}"
FOR_HUMAN="${FOR_HUMAN:-$OVERSEER_HOME/.human}"
REAL_OVERSEER="${REAL_OVERSEER:-$OVERSEER_ROOT}"
WORKSPACE="${WORKSPACE:-$REAL_OVERSEER}"
OPENING_PROMPT="${OPENING_PROMPT:-$REAL_OVERSEER/WAKE.md}"
CODEX_HOME="${CODEX_HOME:-$OVERSEER_HOME/.codex}"
CODEX_CONFIG="${CODEX_CONFIG:-$CODEX_HOME/config.toml}"
CODEX="${CODEX:-$OVERSEER_HOME/.local/bin/codex}"
AUTH_DIR="${AUTH_DIR:-$OVERSEER_HOME/authcreds}"
ACTIVE_AUTH="${ACTIVE_AUTH:-$CODEX_HOME/auth.json}"
OVERSEER_USER="${OVERSEER_USER:-overseer}"
SUDO_BIN="${SUDO_BIN:-/run/wrappers/bin/sudo}"
OVERSEER_PATH="${OVERSEER_PATH:-$OVERSEER_HOME/.local/bin:/run/current-system/sw/bin:/run/wrappers/bin:/usr/bin:/bin}"
DEFAULT_MODEL="${DEFAULT_MODEL:-gpt-5.4}"
DEFAULT_REASONING="${DEFAULT_REASONING:-high}"
STATE_DIR="${STATE_DIR:-$CODEX_HOME/harness-state}"
SESSION_INDEX_JSON="${SESSION_INDEX_JSON:-$STATE_DIR/session-index.json}"
SESSION_INDEX_BIN="${SESSION_INDEX_BIN:-$FOR_HUMAN/scripts/overseer-session-index.py}"
SESSION_SCOPE_DIRS="${SESSION_SCOPE_DIRS:-$WORKSPACE:$OVERSEER_HOME}"
TURN_NOTIFY_BIN="${TURN_NOTIFY_BIN:-$FOR_HUMAN/scripts/overseer-turn-notify.py}"
TURN_NOTIFY_ENABLE="${TURN_NOTIFY_ENABLE:-1}"
TURN_NOTIFY_POLL_INTERVAL="${TURN_NOTIFY_POLL_INTERVAL:-0.5}"
REACHABILITY_CONTACT_BIN="${REACHABILITY_CONTACT_BIN:-$OVERSEER_ROOT/scripts/record_reachability_contact.py}"
REACHABILITY_CONTACT_ENABLE="${REACHABILITY_CONTACT_ENABLE:-1}"
LOAD_BALANCER_BIN="${LOAD_BALANCER_BIN:-$OVERSEER_ROOT/scripts/codex_load_balancer.py}"
LOAD_BALANCER_PYTHON="${LOAD_BALANCER_PYTHON:-/run/current-system/sw/bin/overseer-python3}"
if [[ ! -x "$LOAD_BALANCER_PYTHON" ]]; then
  LOAD_BALANCER_PYTHON="/run/current-system/sw/bin/python3"
fi
if [[ ! -x "$LOAD_BALANCER_PYTHON" ]]; then
  LOAD_BALANCER_PYTHON="$(command -v python3 || true)"
fi
CODEX_LB_ROOT="${CODEX_LB_ROOT:-$OVERSEER_ROOT}"
CODEX_LB_STATE_ROOT="${CODEX_LB_STATE_ROOT:-$CODEX_LB_ROOT/state/codex-load-balancer}"
AUTH_SPEND_PROOF_LATEST="${AUTH_SPEND_PROOF_LATEST:-$CODEX_LB_ROOT/state/auth-spend-proof/latest.json}"
CODEX_LB_AUTH_DIR="${CODEX_LB_AUTH_DIR:-$AUTH_DIR}"
CODEX_LB_QUOTA_READER="${CODEX_LB_QUOTA_READER:-$CODEX_LB_ROOT/scripts/read_codex_usage_quota_best.py}"
CODEX_LB_PYTHON_BIN="${CODEX_LB_PYTHON_BIN:-$LOAD_BALANCER_PYTHON}"
CODEX_LB_QUOTA_PROBE_TIMEOUT_SECONDS="${CODEX_LB_QUOTA_PROBE_TIMEOUT_SECONDS:-20}"
HARNESS_LB_SELECT_TIMEOUT_SECONDS="${HARNESS_LB_SELECT_TIMEOUT_SECONDS:-8}"
AUTH_SPEND_PROBE_SCRIPT="${AUTH_SPEND_PROBE_SCRIPT:-$OVERSEER_ROOT/scripts/probe_auth_spend.py}"
HARNESS_AUTH_SPEND_PREFLIGHT_ENABLE="${HARNESS_AUTH_SPEND_PREFLIGHT_ENABLE:-1}"
HARNESS_AUTH_SPEND_PREFLIGHT_TIMEOUT_SECONDS="${HARNESS_AUTH_SPEND_PREFLIGHT_TIMEOUT_SECONDS:-25}"
AUTH_REPAIR_DEVICE_AUTH_SCRIPT="${AUTH_REPAIR_DEVICE_AUTH_SCRIPT:-$OVERSEER_ROOT/scripts/repair_codex_device_auth.py}"
AUTH_HEALTH_LATEST="${AUTH_HEALTH_LATEST:-$OVERSEER_ROOT/state/auth-health/latest.json}"
HARNESS_REQUESTED_AUTH_REPAIR_ENABLE="${HARNESS_REQUESTED_AUTH_REPAIR_ENABLE:-1}"
HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS="${HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS:-240}"
HARNESS_REQUESTED_AUTH_REPAIR_BROWSER_CONTROL_PATH="${HARNESS_REQUESTED_AUTH_REPAIR_BROWSER_CONTROL_PATH:-playwriter}"
CODEX_RUNTIME_LOCK="${CODEX_RUNTIME_LOCK:-$OVERSEER_ROOT/state/codex-load-balancer/runtime.lock}"
PROVEN_QUOTA_REFRESH_SCRIPT="${PROVEN_QUOTA_REFRESH_SCRIPT:-$OVERSEER_ROOT/scripts/refresh_proven_quota_truth.py}"
PROVEN_QUOTA_REFRESH_PYTHON="${PROVEN_QUOTA_REFRESH_PYTHON:-$LOAD_BALANCER_PYTHON}"
HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE="${HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE:-1}"
HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS="${HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS:-35}"
FZF_BIN="${FZF_BIN:-/run/current-system/sw/bin/fzf}"
HARNESS_FORCE_FZF="${HARNESS_FORCE_FZF:-0}"
PS_BIN="${PS_BIN:-$(command -v ps || true)}"
TIMEOUT_BIN="${TIMEOUT_BIN:-$(command -v timeout || true)}"
HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME="${HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME:-0}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

note() {
  echo "[overseer-harness] $*"
}

current_user() {
  if [[ -n "${HARNESS_CURRENT_USER:-}" ]]; then
    printf '%s\n' "$HARNESS_CURRENT_USER"
  else
    id -un
  fi
}

reexec_as_overseer() {
  local script_path="$1"
  shift || true

  if [[ "$(current_user)" == "$OVERSEER_USER" ]]; then
    return
  fi

  local -a clean_env
  clean_env=(
    env
    -i
    HOME="$OVERSEER_HOME"
    PATH="$OVERSEER_PATH"
    TERM="${TERM:-xterm-256color}"
    USER="$OVERSEER_USER"
    LOGNAME="$OVERSEER_USER"
    SHELL="/run/current-system/sw/bin/bash"
    OVERSEER_HOME="$OVERSEER_HOME"
    OVERSEER_ROOT="$OVERSEER_ROOT"
    FOR_HUMAN="$FOR_HUMAN"
    REAL_OVERSEER="$REAL_OVERSEER"
    WORKSPACE="$WORKSPACE"
    OPENING_PROMPT="$OPENING_PROMPT"
    CODEX_HOME="$CODEX_HOME"
    CODEX_CONFIG="$CODEX_CONFIG"
    CODEX="$CODEX"
    AUTH_DIR="$AUTH_DIR"
    ACTIVE_AUTH="$ACTIVE_AUTH"
    OVERSEER_USER="$OVERSEER_USER"
    SUDO_BIN="$SUDO_BIN"
    OVERSEER_PATH="$OVERSEER_PATH"
    DEFAULT_MODEL="$DEFAULT_MODEL"
    DEFAULT_REASONING="$DEFAULT_REASONING"
    STATE_DIR="$STATE_DIR"
    SESSION_INDEX_JSON="$SESSION_INDEX_JSON"
    SESSION_INDEX_BIN="$SESSION_INDEX_BIN"
    SESSION_SCOPE_DIRS="$SESSION_SCOPE_DIRS"
    TURN_NOTIFY_BIN="$TURN_NOTIFY_BIN"
    TURN_NOTIFY_ENABLE="$TURN_NOTIFY_ENABLE"
    TURN_NOTIFY_POLL_INTERVAL="$TURN_NOTIFY_POLL_INTERVAL"
    REACHABILITY_CONTACT_BIN="$REACHABILITY_CONTACT_BIN"
    REACHABILITY_CONTACT_ENABLE="$REACHABILITY_CONTACT_ENABLE"
    LOAD_BALANCER_BIN="$LOAD_BALANCER_BIN"
    LOAD_BALANCER_PYTHON="$LOAD_BALANCER_PYTHON"
    CODEX_RUNTIME_LOCK="$CODEX_RUNTIME_LOCK"
    PROVEN_QUOTA_REFRESH_SCRIPT="$PROVEN_QUOTA_REFRESH_SCRIPT"
    PROVEN_QUOTA_REFRESH_PYTHON="$PROVEN_QUOTA_REFRESH_PYTHON"
    PROVEN_REFRESH_LOG="${PROVEN_REFRESH_LOG:-}"
    HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE="$HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE"
    HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS="$HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS"
    CODEX_LB_ROOT="$CODEX_LB_ROOT"
    CODEX_LB_STATE_ROOT="$CODEX_LB_STATE_ROOT"
    CODEX_LB_AUTH_DIR="$CODEX_LB_AUTH_DIR"
    CODEX_LB_QUOTA_READER="$CODEX_LB_QUOTA_READER"
    CODEX_LB_PYTHON_BIN="$CODEX_LB_PYTHON_BIN"
    CODEX_LB_QUOTA_PROBE_TIMEOUT_SECONDS="$CODEX_LB_QUOTA_PROBE_TIMEOUT_SECONDS"
    HARNESS_LB_SELECT_TIMEOUT_SECONDS="$HARNESS_LB_SELECT_TIMEOUT_SECONDS"
    AUTH_SPEND_PROBE_SCRIPT="$AUTH_SPEND_PROBE_SCRIPT"
    HARNESS_AUTH_SPEND_PREFLIGHT_ENABLE="$HARNESS_AUTH_SPEND_PREFLIGHT_ENABLE"
    HARNESS_AUTH_SPEND_PREFLIGHT_TIMEOUT_SECONDS="$HARNESS_AUTH_SPEND_PREFLIGHT_TIMEOUT_SECONDS"
    AUTH_REPAIR_DEVICE_AUTH_SCRIPT="$AUTH_REPAIR_DEVICE_AUTH_SCRIPT"
    AUTH_HEALTH_LATEST="$AUTH_HEALTH_LATEST"
    HARNESS_REQUESTED_AUTH_REPAIR_ENABLE="$HARNESS_REQUESTED_AUTH_REPAIR_ENABLE"
    HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS="$HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS"
    HARNESS_REQUESTED_AUTH_REPAIR_BROWSER_CONTROL_PATH="$HARNESS_REQUESTED_AUTH_REPAIR_BROWSER_CONTROL_PATH"
    CODEX_LB_PROFILES="${CODEX_LB_PROFILES:-}"
    CODEX_LB_QUOTA_FRESH_SECONDS="${CODEX_LB_QUOTA_FRESH_SECONDS:-900}"
    CODEX_LB_INTERACTIVE_TTL_SECONDS="${CODEX_LB_INTERACTIVE_TTL_SECONDS:-43200}"
    CODEX_LB_DAEMON_TTL_SECONDS="${CODEX_LB_DAEMON_TTL_SECONDS:-21600}"
    CODEX_LB_MIN_REMAINING_PERCENT="${CODEX_LB_MIN_REMAINING_PERCENT:-1}"
    TIMEOUT_BIN="$TIMEOUT_BIN"
    FZF_BIN="$FZF_BIN"
    HARNESS_FORCE_FZF="$HARNESS_FORCE_FZF"
    HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME="$HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME"
    HARNESS_CURRENT_USER="$OVERSEER_USER"
  )

  if [[ -n "${LANG:-}" ]]; then
    clean_env+=(LANG="$LANG")
  fi
  if [[ -n "${LC_ALL:-}" ]]; then
    clean_env+=(LC_ALL="$LC_ALL")
  fi
  if [[ -n "${TZ:-}" ]]; then
    clean_env+=(TZ="$TZ")
  fi

  exec "$SUDO_BIN" -u "$OVERSEER_USER" "${clean_env[@]}" "$script_path" "$@"
}

ensure_state_dir() {
  mkdir -p "$STATE_DIR"
}

require_file() {
  local path="$1"
  [[ -f "$path" ]] || die "required file not found: $path"
}

require_dir() {
  local path="$1"
  [[ -d "$path" ]] || die "required directory not found: $path"
}

check_launch_deps() {
  require_dir "$WORKSPACE"
  require_dir "$AUTH_DIR"
  [[ -x "$CODEX" ]] || die "codex not found at $CODEX"
  [[ -x "$SUDO_BIN" ]] || die "sudo not found at $SUDO_BIN"
  [[ -x "$SESSION_INDEX_BIN" ]] || die "session index tool not found at $SESSION_INDEX_BIN"
  [[ -x "$TURN_NOTIFY_BIN" ]] || die "turn notifier not found at $TURN_NOTIFY_BIN"
  [[ -f "$LOAD_BALANCER_BIN" ]] || die "load balancer not found at $LOAD_BALANCER_BIN"
  if [[ "$HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE" -eq 1 ]]; then
    [[ -f "$PROVEN_QUOTA_REFRESH_SCRIPT" ]] || die "near-supply self-heal script not found at $PROVEN_QUOTA_REFRESH_SCRIPT"
  fi
  command -v jq >/dev/null 2>&1 || die "jq is required"
  command -v flock >/dev/null 2>&1 || die "flock is required"
  ensure_state_dir
  if [[ ! -f "$ACTIVE_AUTH" ]] && ! compgen -G "$AUTH_DIR/*.auth.json" >/dev/null; then
    die "no auth material available: missing $ACTIVE_AUTH and no bundles under $AUTH_DIR"
  fi
}

requested_profile_preflight_probe() {
  local requested_profile="${1:-}"
  [[ -n "$requested_profile" ]] || return 1
  "$LOAD_BALANCER_PYTHON" "$AUTH_SPEND_PROBE_SCRIPT" \
    --profiles "$requested_profile" \
    --timeout-seconds "$HARNESS_AUTH_SPEND_PREFLIGHT_TIMEOUT_SECONDS" \
    --json-only
}

requested_profile_is_deactivated() {
  local requested_profile="${1:-}"
  [[ -n "$requested_profile" ]] || return 1
  [[ -f "$AUTH_HEALTH_LATEST" ]] || return 1
  jq -e --arg profile "$requested_profile" '
    (
      (.summary.operator_reported_deactivated_profiles // [])
      | map(select(type == "string"))
      | index($profile)
    ) != null
    or
    any(
      .issues[]?;
      (.kind // "") == "operator_reported_account_deactivated" and (.profile // "") == $profile
    )
  ' "$AUTH_HEALTH_LATEST" >/dev/null 2>&1
}

run_requested_profile_auth_repair() {
  local requested_profile="${1:-}"
  [[ -n "$requested_profile" ]] || return 1
  [[ "$HARNESS_REQUESTED_AUTH_REPAIR_ENABLE" -eq 1 ]] || return 1
  [[ -f "$AUTH_REPAIR_DEVICE_AUTH_SCRIPT" ]] || return 1
  if requested_profile_is_deactivated "$requested_profile"; then
    echo "[overseer-harness] requested profile $requested_profile is operator-reported deactivated; skipping bounded auth repair" >&2
    return 1
  fi

  local -a command
  command=(
    "$LOAD_BALANCER_PYTHON"
    "$AUTH_REPAIR_DEVICE_AUTH_SCRIPT"
    --profile "$requested_profile"
    --browser-control-path "$HARNESS_REQUESTED_AUTH_REPAIR_BROWSER_CONTROL_PATH"
    --json
  )

  local payload="" rc=0
  set +e
  if [[ -n "$TIMEOUT_BIN" && -x "$TIMEOUT_BIN" && "$HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS" =~ ^[0-9]+$ && "$HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS" -gt 0 ]]; then
    payload="$("$TIMEOUT_BIN" --foreground "${HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS}s" "${command[@]}")"
    rc=$?
  else
    payload="$("${command[@]}")"
    rc=$?
  fi
  set -e

  if [[ "$rc" -eq 124 || "$rc" -eq 137 ]]; then
    echo "[overseer-harness] requested profile $requested_profile auth repair timed out after ${HARNESS_REQUESTED_AUTH_REPAIR_TIMEOUT_SECONDS}s" >&2
    return 1
  fi
  if [[ "$rc" -ne 0 || -z "$payload" ]]; then
    echo "[overseer-harness] requested profile $requested_profile auth repair failed to return usable JSON" >&2
    return 1
  fi

  local repair_status
  repair_status="$(jq -r '.status // empty' <<<"$payload" 2>/dev/null || true)"
  if [[ "$repair_status" == "ok" ]]; then
    echo "[overseer-harness] spent bounded requested-profile auth repair on $requested_profile" >&2
    return 0
  fi

  echo "[overseer-harness] requested profile $requested_profile auth repair did not restore viability ($repair_status)" >&2
  return 1
}

requested_profile_after_auth_preflight() {
  local requested_profile="${1:-}"
  [[ -n "$requested_profile" ]] || return 0
  [[ "$HARNESS_AUTH_SPEND_PREFLIGHT_ENABLE" -eq 1 ]] || {
    printf '%s\n' "$requested_profile"
    return 0
  }
  [[ -f "$AUTH_SPEND_PROBE_SCRIPT" ]] || {
    printf '%s\n' "$requested_profile"
    return 0
  }

  local probe_json=""
  local rc=0
  set +e
  probe_json="$(requested_profile_preflight_probe "$requested_profile")"
  rc=$?
  set -e

  [[ -n "$probe_json" ]] || {
    printf '%s\n' "$requested_profile"
    return 0
  }

  local auth_invalid_count
  auth_invalid_count="$(
    jq -r --arg profile "$requested_profile" '
      [ .results[]? | select(.profile == $profile and (.failure_classification.class // "") == "auth_invalid") ]
      | length
    ' <<<"$probe_json" 2>/dev/null || printf '0'
  )"
  if [[ "$auth_invalid_count" != "0" ]]; then
    if run_requested_profile_auth_repair "$requested_profile"; then
      set +e
      probe_json="$(requested_profile_preflight_probe "$requested_profile")"
      rc=$?
      set -e
      if [[ -n "$probe_json" ]]; then
        auth_invalid_count="$(
          jq -r --arg profile "$requested_profile" '
            [ .results[]? | select(.profile == $profile and (.failure_classification.class // "") == "auth_invalid") ]
            | length
          ' <<<"$probe_json" 2>/dev/null || printf '0'
        )"
        if [[ "$auth_invalid_count" == "0" ]]; then
          printf '%s\n' "$requested_profile"
          return "$rc"
        fi
      fi
    fi
    echo "[overseer-harness] requested profile $requested_profile failed direct auth preflight; clearing explicit request for automatic failover" >&2
    return 0
  fi

  printf '%s\n' "$requested_profile"
  return "$rc"
}

check_install_deps() {
  command -v jq >/dev/null 2>&1 || die "jq is required"
  ensure_state_dir
}

switch_profile() {
  local profile="${1:-}"
  local src="$AUTH_DIR/$profile.auth.json"
  [[ -f "$src" ]] || die "profile not found: $src"
  local active_dir tmp
  active_dir="$(dirname "$ACTIVE_AUTH")"
  mkdir -p "$active_dir"
  tmp="$(mktemp "$active_dir/.auth.json.tmp.XXXXXX")"
  install -m 600 "$src" "$tmp"
  mv -f "$tmp" "$ACTIVE_AUTH"
  chmod 600 "$ACTIVE_AUTH"
  printf '%s\n' "$profile" > "$STATE_DIR/last-profile"
  note "switched auth profile to $profile"
}

ensure_codex_config_defaults() {
  mkdir -p "$CODEX_HOME"

  if [[ ! -f "$CODEX_CONFIG" ]]; then
    cat > "$CODEX_CONFIG" <<'EOF'
model = "gpt-5.4"
model_reasoning_effort = "high"
approval_policy = "never"
sandbox_permissions = ["disk-full-read-access", "disk-full-write-access", "network"]

[shell_environment_policy]
inherit = "all"

[tui]
status_line = ["model-with-reasoning", "context-remaining", "current-dir", "five-hour-limit", "weekly-limit", "total-input-tokens", "total-output-tokens", "session-id"]
EOF
    return
  fi

  if ! grep -q '^model = "gpt-5.4"$' "$CODEX_CONFIG"; then
    printf '\nmodel = "gpt-5.4"\n' >> "$CODEX_CONFIG"
  fi

  if ! grep -q '^model_reasoning_effort = "high"$' "$CODEX_CONFIG"; then
    printf 'model_reasoning_effort = "high"\n' >> "$CODEX_CONFIG"
  fi

  if ! grep -q '^approval_policy = "never"$' "$CODEX_CONFIG"; then
    printf 'approval_policy = "never"\n' >> "$CODEX_CONFIG"
  fi

  if ! grep -q '^sandbox_permissions = \["disk-full-read-access", "disk-full-write-access", "network"\]$' "$CODEX_CONFIG"; then
    printf 'sandbox_permissions = ["disk-full-read-access", "disk-full-write-access", "network"]\n' >> "$CODEX_CONFIG"
  fi

  if ! grep -q '^\[shell_environment_policy\]$' "$CODEX_CONFIG"; then
    printf '\n[shell_environment_policy]\ninherit = "all"\n' >> "$CODEX_CONFIG"
  elif ! grep -q '^inherit = "all"$' "$CODEX_CONFIG"; then
    printf 'inherit = "all"\n' >> "$CODEX_CONFIG"
  fi

  if ! grep -q '^status_line = \["model-with-reasoning", "context-remaining", "current-dir", "five-hour-limit", "weekly-limit", "total-input-tokens", "total-output-tokens", "session-id"\]$' "$CODEX_CONFIG"; then
    printf '\n[tui]\nstatus_line = ["model-with-reasoning", "context-remaining", "current-dir", "five-hour-limit", "weekly-limit", "total-input-tokens", "total-output-tokens", "session-id"]\n' >> "$CODEX_CONFIG"
  fi
}

codex_base_args() {
  printf '%s\n' \
    "--dangerously-bypass-approvals-and-sandbox" \
    "--search" \
    "--model" "$DEFAULT_MODEL" \
    "-c" "model_reasoning_effort=\"$DEFAULT_REASONING\""
}

launch_codex() {
  local subcommand="${1:-}"
  shift || true

  local -a args
  mapfile -t args < <(codex_base_args)
  args+=(-C "$WORKSPACE")

  if [[ -n "$subcommand" ]]; then
    args=("$subcommand" "${args[@]}")
  fi

  local -a command
  if [[ "$(current_user)" == "$OVERSEER_USER" ]]; then
    command=(env \
      HOME="$OVERSEER_HOME" \
      PATH="$OVERSEER_PATH" \
      CODEX_HOME="$CODEX_HOME" \
      "$CODEX" "${args[@]}" "$@")
  else
    command=("$SUDO_BIN" -u "$OVERSEER_USER" env \
      HOME="$OVERSEER_HOME" \
      PATH="$OVERSEER_PATH" \
      CODEX_HOME="$CODEX_HOME" \
      HARNESS_CURRENT_USER="$OVERSEER_USER" \
      "$CODEX" "${args[@]}" "$@")
  fi

  "${command[@]}"
}

run_with_codex_runtime_lock() {
  local lock_dir
  lock_dir="$(dirname "$CODEX_RUNTIME_LOCK")"
  mkdir -p "$lock_dir"
  exec 9>"$CODEX_RUNTIME_LOCK"
  flock 9
  "$@"
}

find_live_local_resume_processes() {
  local session_id="${1:-}"
  [[ -n "$session_id" ]] || return 0
  [[ -n "$PS_BIN" && -x "$PS_BIN" ]] || return 0

  local current_pid="$$"
  "$PS_BIN" -eo pid=,ppid=,tty=,user=,args= 2>/dev/null | while read -r pid ppid tty user args; do
    [[ -n "$pid" ]] || continue
    [[ "$pid" != "$current_pid" ]] || continue
    [[ "$args" == *"codex resume"* ]] || continue
    [[ "$args" == *"$session_id"* ]] || continue
    printf '%s\t%s\t%s\t%s\t%s\n' "$pid" "$ppid" "$tty" "$user" "$args"
  done
}

reclaimable_orphan_resume_process() {
  local pid="${1:-}"
  local ppid="${2:-}"
  local tty="${3:-}"

  [[ -n "$pid" && -n "$ppid" && -n "$tty" ]] || return 1
  [[ "$ppid" == "1" ]] || return 1
  [[ "$tty" == "?" ]] || return 1
  return 0
}

reap_orphan_resume_process() {
  local pid="${1:-}"
  [[ -n "$pid" ]] || return 1

  kill -TERM "$pid" >/dev/null 2>&1 || true
  sleep 1
  if kill -0 "$pid" >/dev/null 2>&1; then
    kill -KILL "$pid" >/dev/null 2>&1 || true
    sleep 1
  fi

  ! kill -0 "$pid" >/dev/null 2>&1
}

guard_against_duplicate_local_resume() {
  local session_id="${1:-}"
  [[ -n "$session_id" ]] || return 0

  local duplicates
  duplicates="$(find_live_local_resume_processes "$session_id" || true)"
  [[ -z "$duplicates" ]] && return 0

  local first
  first="$(printf '%s\n' "$duplicates" | head -n 1)"
  local pid ppid tty user args
  IFS=$'\t' read -r pid ppid tty user args <<<"$first"

  if reclaimable_orphan_resume_process "$pid" "$ppid" "$tty"; then
    if reap_orphan_resume_process "$pid"; then
      note "reclaimed orphaned detached resume for $session_id (pid=$pid)"
      return 0
    fi
    die "session $session_id has an orphaned detached resume process (pid=$pid) that could not be reclaimed automatically"
  fi

  die "session $session_id already has a live local resume process (pid=$pid user=$user); keep using the first terminal or end that resume before starting another"
}

turn_notifier_scope_args() {
  local item
  IFS=':' read -r -a scope_items <<< "$SESSION_SCOPE_DIRS"
  for item in "${scope_items[@]}"; do
    [[ -n "$item" ]] || continue
    printf '%s\0' "--scope-dir" "$item"
  done
}

start_turn_notifier() {
  local session_id="${1:-}"
  [[ "$TURN_NOTIFY_ENABLE" -eq 1 ]] || return 0
  [[ -t 1 ]] || return 0

  local -a args
  args=(
    "$TURN_NOTIFY_BIN"
    "--sessions-root" "$CODEX_HOME/sessions"
    "--workspace" "$WORKSPACE"
    "--poll-interval" "$TURN_NOTIFY_POLL_INTERVAL"
    "--start-time" "$(date +%s.%N)"
  )

  if [[ -n "$session_id" ]]; then
    args+=("--session-id" "$session_id")
  fi

  while IFS= read -r -d '' token; do
    args+=("$token")
  done < <(turn_notifier_scope_args)

  "${args[@]}" &
  HARNESS_TURN_NOTIFY_PID=$!
}

stop_turn_notifier() {
  if [[ -n "${HARNESS_TURN_NOTIFY_PID:-}" ]]; then
    kill "$HARNESS_TURN_NOTIFY_PID" >/dev/null 2>&1 || true
    wait "$HARNESS_TURN_NOTIFY_PID" >/dev/null 2>&1 || true
    unset HARNESS_TURN_NOTIFY_PID
  fi
}

run_with_turn_notifier() {
  local session_id="${1:-}"
  shift || true

  start_turn_notifier "$session_id"
  trap stop_turn_notifier EXIT
  set +e
  run_with_codex_runtime_lock "$@"
  local rc=$?
  set -e
  stop_turn_notifier
  trap - EXIT
  return "$rc"
}

compose_opening_prompt() {
  local extra_prompt="${1:-}"
  [[ -f "$OPENING_PROMPT" ]] || die "wake document not found: $OPENING_PROMPT"

  local opening_text
  opening_text="$(cat "$OPENING_PROMPT")"

  if [[ -n "$extra_prompt" ]]; then
    printf '%s\n\nOperator note:\n%s\n' "$opening_text" "$extra_prompt"
  else
    printf '%s\n' "$opening_text"
  fi
}

compose_cold_required_resume_prompt() {
  local previous_session_id="$1"
  local continuity_reason="$2"
  local prompt="${3:-}"
  [[ -f "$OPENING_PROMPT" ]] || die "wake document not found: $OPENING_PROMPT"

  local opening_text
  opening_text="$(cat "$OPENING_PROMPT")"

  printf 'COLD-REQUIRED RESUME DEMOTION\n'
  printf '============================\n\n'
  printf 'This is a fresh session, not a resume of %s.\n' "$previous_session_id"
  printf 'The load balancer marked the requested reopen cold-required (%s).\n' "$continuity_reason"
  printf 'Use this session as a fresh continuation on the selected profile instead of assuming old-session continuity.\n\n'
  printf '%s\n' "$opening_text"
  if [[ -n "$prompt" ]]; then
    printf '\nOriginal operator note:\n%s\n' "$prompt"
  fi
}

read_last_profile() {
  local path="$STATE_DIR/last-profile"
  if [[ -f "$path" ]]; then
    tr -d '\n' < "$path"
  fi
}

active_auth_profile_name_local() {
  [[ -f "$ACTIVE_AUTH" ]] || return 0
  command -v sha256sum >/dev/null 2>&1 || return 0
  command -v jq >/dev/null 2>&1 || return 0

  local active_fingerprint
  active_fingerprint="$(sha256sum "$ACTIVE_AUTH" | awk '{print $1}')"
  local active_account_id
  active_account_id="$(jq -r '.tokens.account_id // empty' "$ACTIVE_AUTH" 2>/dev/null || true)"

  local unique_account_match=""
  local src profile fingerprint account_id
  for src in "$AUTH_DIR"/*.auth.json; do
    [[ -f "$src" ]] || continue
    profile="$(basename "$src" .auth.json)"
    fingerprint="$(sha256sum "$src" | awk '{print $1}')"
    if [[ -n "$active_fingerprint" && "$fingerprint" == "$active_fingerprint" ]]; then
      printf '%s\n' "$profile"
      return 0
    fi
    if [[ -n "$active_account_id" ]]; then
      account_id="$(jq -r '.tokens.account_id // empty' "$src" 2>/dev/null || true)"
      if [[ "$account_id" == "$active_account_id" ]]; then
        if [[ -n "$unique_account_match" && "$unique_account_match" != "$profile" ]]; then
          unique_account_match=""
          break
        fi
        unique_account_match="$profile"
      fi
    fi
  done

  if [[ -n "$unique_account_match" ]]; then
    printf '%s\n' "$unique_account_match"
  fi
}

bound_profile_for_session_local() {
  local session_id="${1:-}"
  local bindings_path="$CODEX_LB_STATE_ROOT/session-bindings.json"
  [[ -n "$session_id" && -f "$bindings_path" ]] || return 0
  jq -r --arg session_id "$session_id" '.sessions[$session_id].bound_profile // empty' "$bindings_path" 2>/dev/null || true
}

rescue_profile_is_spend_invalid_local() {
  local profile="${1:-}"
  [[ -n "$profile" ]] || return 1
  command -v jq >/dev/null 2>&1 || return 1
  [[ -f "$AUTH_SPEND_PROOF_LATEST" ]] || return 1
  [[ -f "$AUTH_DIR/$profile.auth.json" ]] || return 1

  local proof_status failure_class measured_at bundle_last_refresh
  proof_status="$(
    jq -r --arg profile "$profile" '
      [ .results[]? | select(.profile == $profile) ]
      | sort_by(.completed_at // "")
      | (last // {})
      | .status // empty
    ' "$AUTH_SPEND_PROOF_LATEST" 2>/dev/null || true
  )"
  failure_class="$(
    jq -r --arg profile "$profile" '
      [ .results[]? | select(.profile == $profile) ]
      | sort_by(.completed_at // "")
      | (last // {})
      | .failure_classification.class // empty
    ' "$AUTH_SPEND_PROOF_LATEST" 2>/dev/null || true
  )"
  measured_at="$(
    jq -r --arg profile "$profile" '
      [ .results[]? | select(.profile == $profile) ]
      | sort_by(.completed_at // "")
      | (last // {})
      | .completed_at // empty
    ' "$AUTH_SPEND_PROOF_LATEST" 2>/dev/null || true
  )"

  [[ "$proof_status" != "ok" ]] || return 1
  [[ "$failure_class" == "auth_invalid" ]] || return 1

  bundle_last_refresh="$(jq -r '.last_refresh // empty' "$AUTH_DIR/$profile.auth.json" 2>/dev/null || true)"
  if [[ -n "$bundle_last_refresh" && -n "$measured_at" && "$bundle_last_refresh" > "$measured_at" ]]; then
    return 1
  fi

  return 0
}

rescue_profile_candidates() {
  local session_id="${1:-}"
  local requested_profile="${2:-}"
  local candidate
  local -A seen=()
  for candidate in \
    "$requested_profile" \
    "$(bound_profile_for_session_local "$session_id")" \
    "$(active_auth_profile_name_local)" \
    "$(read_last_profile || true)"
  do
    [[ -n "$candidate" ]] || continue
    [[ -f "$AUTH_DIR/$candidate.auth.json" ]] || continue
    if rescue_profile_is_spend_invalid_local "$candidate"; then
      continue
    fi
    if [[ -n "${seen[$candidate]:-}" ]]; then
      continue
    fi
    seen[$candidate]=1
    printf '%s\n' "$candidate"
  done
}

near_supply_rescue_candidates_from_lb_json() {
  local payload="${1:-}"
  [[ -n "$payload" ]] || return 0
  jq -r '
    .near_supply_profiles // []
    | map(select(type == "string"))
    | .[]
  ' <<<"$payload" 2>/dev/null || true
}

near_supply_action_is_auto_healable() {
  case "${1:-}" in
    claim_playwriter_desktop_lane|attach_playwriter_tab|launch_playwriter_profile|restart_playwriter_profile|install_or_stage_playwriter_extension)
      return 0
      ;;
  esac
  return 1
}

near_supply_self_heal_candidates_from_lb_json() {
  local payload="${1:-}"
  [[ "$HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE" -eq 1 ]] || return 0
  [[ -n "$payload" ]] || return 0
  jq -r '
    if (.status // "") == "ok" and (.selected_posture // "") == "near_supply_browser_recovery" then
      [(.selected_profile // ""), (.recommended_action // "")]
      | @tsv
    elif (.status // "") == "no_profile_available" then
      .near_supply_details // {}
      | to_entries[]
      | select(.key | type == "string")
      | [.key, (.value.action // "")]
      | @tsv
    else
      empty
    end
  ' <<<"$payload" 2>/dev/null | while IFS=$'\t' read -r profile action; do
    [[ -n "$profile" ]] || continue
    near_supply_action_is_auto_healable "$action" || continue
    printf '%s\n' "$profile"
  done
}

run_near_supply_self_heal() {
  [[ "$HARNESS_NEAR_SUPPLY_SELF_HEAL_ENABLE" -eq 1 ]] || return 1
  [[ -f "$PROVEN_QUOTA_REFRESH_SCRIPT" ]] || return 1

  local -a profiles=("$@")
  [[ "${#profiles[@]}" -gt 0 ]] || return 1

  local profiles_csv
  profiles_csv="$(IFS=,; printf '%s' "${profiles[*]}")"
  local -a command
  command=(
    "$PROVEN_QUOTA_REFRESH_PYTHON"
    "$PROVEN_QUOTA_REFRESH_SCRIPT"
    --profiles "$profiles_csv"
    --timeout-seconds "$HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS"
    --json
  )

  local payload="" rc=0
  set +e
  if [[ -n "$TIMEOUT_BIN" && -x "$TIMEOUT_BIN" && "$HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS" =~ ^[0-9]+$ && "$HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS" -gt 0 ]]; then
    payload="$("$TIMEOUT_BIN" --foreground "${HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS}s" "${command[@]}")"
    rc=$?
  else
    payload="$("${command[@]}")"
    rc=$?
  fi
  set -e

  if [[ "$rc" -eq 124 || "$rc" -eq 137 ]]; then
    note "near-supply self-heal timed out for $profiles_csv after ${HARNESS_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS}s"
    return 1
  fi
  if [[ "$rc" -ne 0 || -z "$payload" ]]; then
    note "near-supply self-heal failed for $profiles_csv"
    return 1
  fi

  local refresh_status refreshed_profiles
  refresh_status="$(jq -r '.status // empty' <<<"$payload" 2>/dev/null || true)"
  refreshed_profiles="$(
    jq -r '
      (.refreshed_profiles // [])
      | map(select(type == "string"))
      | join(",")
    ' <<<"$payload" 2>/dev/null || true
  )"
  if [[ -n "$refreshed_profiles" ]]; then
    note "spent bounded near-supply self-heal on $profiles_csv ($refresh_status; refreshed=$refreshed_profiles)"
  else
    note "spent bounded near-supply self-heal on $profiles_csv ($refresh_status)"
  fi
  return 0
}

load_balancer_json() {
  local command="$1"
  shift || true
  "$LOAD_BALANCER_PYTHON" "$LOAD_BALANCER_BIN" "$command" --json-only "$@"
}

select_load_balancer_json() {
  local mode="$1"
  shift || true
  local -a args=("$@")
  local payload=""
  local rc
  local cache_payload=""
  local cache_status=""

  if [[ "$mode" == "resume" ]]; then
    set +e
    cache_payload="$(load_balancer_json "${args[@]}" --no-allow-probe)"
    rc=$?
    set -e
    if [[ "$rc" -eq 0 ]]; then
      cache_status="$(jq -r '.status' <<<"$cache_payload")"
    fi
    if [[ "$rc" -eq 0 && "$cache_status" == "ok" ]]; then
      local selected_profile bound_profile fresh selection_reason
      selected_profile="$(jq -r '.selected_profile // empty' <<<"$cache_payload")"
      bound_profile="$(jq -r '.bound_profile // empty' <<<"$cache_payload")"
      fresh="$(jq -r '.quota_snapshot.fresh // false' <<<"$cache_payload")"
      selection_reason="$(jq -r '.selection_reason // empty' <<<"$cache_payload")"
      if [[ "$selection_reason" == "requested_profile_forced" || "$selection_reason" == "requested_profile_available" ]]; then
        printf '%s\n' "$cache_payload"
        return 0
      fi
      if [[ -n "$selected_profile" && "$selected_profile" == "$bound_profile" && "$fresh" != "true" ]]; then
        :
      else
        printf '%s\n' "$cache_payload"
        return 0
      fi
    fi
  fi

  if [[ -n "$TIMEOUT_BIN" && -x "$TIMEOUT_BIN" && "$HARNESS_LB_SELECT_TIMEOUT_SECONDS" =~ ^[0-9]+$ && "$HARNESS_LB_SELECT_TIMEOUT_SECONDS" -gt 0 ]]; then
    set +e
    payload="$("$TIMEOUT_BIN" --foreground "${HARNESS_LB_SELECT_TIMEOUT_SECONDS}s" "$LOAD_BALANCER_PYTHON" "$LOAD_BALANCER_BIN" "${args[@]}" --json-only)"
    rc=$?
    set -e
    if [[ "$rc" -eq 124 || "$rc" -eq 137 ]]; then
      if [[ "$mode" == "resume" && "$cache_status" == "ok" ]]; then
        echo "[overseer-harness] load balancer reprobe timed out after ${HARNESS_LB_SELECT_TIMEOUT_SECONDS}s; falling back to cache-only resume selection" >&2
        jq --argjson timeout_seconds "$HARNESS_LB_SELECT_TIMEOUT_SECONDS" '.probe_timeout_fallback = true | .probe_timeout_seconds = $timeout_seconds' <<<"$cache_payload"
        return 0
      fi
      return "$rc"
    fi
    if [[ "$rc" -eq 0 ]]; then
      printf '%s\n' "$payload"
      return 0
    fi
  fi

  load_balancer_json "${args[@]}"
}

record_reachability_contact() {
  local event_kind="$1"
  local requested_profile="${2:-}"
  local session_ref="${3:-}"
  [[ "$REACHABILITY_CONTACT_ENABLE" -eq 1 ]] || return 0
  [[ -x "$REACHABILITY_CONTACT_BIN" ]] || return 0

  local -a args
  args=(
    "$REACHABILITY_CONTACT_BIN"
    "--event-kind" "$event_kind"
    "--workspace" "$WORKSPACE"
    "--current-user" "$(current_user)"
  )
  if [[ -n "$requested_profile" ]]; then
    args+=("--requested-profile" "$requested_profile")
  fi
  if [[ -n "$session_ref" ]]; then
    args+=("--session-ref" "$session_ref")
  fi
  if [[ -n "${HARNESS_LB_PROFILE:-}" ]]; then
    args+=("--selected-profile" "$HARNESS_LB_PROFILE")
  fi

  "${args[@]}" >/dev/null 2>&1 || true
}

select_load_balanced_profile() {
  local mode="$1"
  local session_id="${2:-}"
  local requested_profile="${3:-}"
  local consumer_id="$4"
  local effective_requested_profile="$requested_profile"
  if [[ -n "$requested_profile" ]]; then
    effective_requested_profile="$(requested_profile_after_auth_preflight "$requested_profile")"
  fi
  local last_profile
  last_profile="$(read_last_profile || true)"

  local -a args
  args=(
    select
    --consumer-kind interactive
    --consumer-id "$consumer_id"
    --mode "$mode"
  )

  if [[ -n "$session_id" ]]; then
    args+=(--session-id "$session_id")
  fi
  if [[ -n "$effective_requested_profile" ]]; then
    args+=(--requested-profile "$effective_requested_profile")
  fi
  if [[ -n "$last_profile" ]]; then
    args+=(--last-profile "$last_profile")
  fi
  args+=(--process-id "$$")
  local lb_rc=0
  set +e
  HARNESS_LB_JSON="$(select_load_balancer_json "$mode" "${args[@]}")"
  lb_rc=$?
  set -e
  if [[ "$lb_rc" -ne 0 && -z "${HARNESS_LB_JSON:-}" ]]; then
    die "load balancer selection failed"
  fi
  local lb_status
  lb_status="$(jq -r '.status' <<<"$HARNESS_LB_JSON")"
  if [[ "$lb_status" != "ok" ]]; then
    local lb_reason rescue_profile rescue_json rescue_status
    lb_reason="$(jq -r '.reason // .status' <<<"$HARNESS_LB_JSON")"
    local -a self_heal_profiles=()
    while IFS= read -r rescue_profile; do
      [[ -n "$rescue_profile" ]] || continue
      self_heal_profiles+=("$rescue_profile")
    done < <(
      near_supply_self_heal_candidates_from_lb_json "$HARNESS_LB_JSON" | awk 'NF && !seen[$0]++'
    )
    if [[ "${#self_heal_profiles[@]}" -gt 0 ]]; then
      if run_near_supply_self_heal "${self_heal_profiles[@]}"; then
        local heal_json=""
        set +e
        heal_json="$(select_load_balancer_json "$mode" "${args[@]}")"
        lb_rc=$?
        set -e
        if [[ "$lb_rc" -eq 0 && -n "$heal_json" ]]; then
          HARNESS_LB_JSON="$heal_json"
          lb_status="$(jq -r '.status' <<<"$HARNESS_LB_JSON")"
          lb_reason="$(jq -r '.reason // .status' <<<"$HARNESS_LB_JSON")"
        fi
      fi
    fi
    if [[ "$mode" == "resume" && -z "$requested_profile" && "$lb_status" == "no_profile_available" ]]; then
      while IFS= read -r rescue_profile; do
        [[ -n "$rescue_profile" ]] || continue
        local -a rescue_args=("${args[@]}" --requested-profile "$rescue_profile" --no-allow-probe)
        set +e
        rescue_json="$(load_balancer_json "${rescue_args[@]}")"
        lb_rc=$?
        set -e
        if [[ "$lb_rc" -ne 0 || -z "$rescue_json" ]]; then
          continue
        fi
        rescue_status="$(jq -r '.status' <<<"$rescue_json")"
        if [[ "$rescue_status" == "ok" ]]; then
          note "load balancer entered local-rescue mode on $rescue_profile after $lb_reason"
          HARNESS_LB_JSON="$rescue_json"
          lb_status="$rescue_status"
          break
        fi
      done < <(
        {
          rescue_profile_candidates "$session_id" "$requested_profile"
          near_supply_rescue_candidates_from_lb_json "$HARNESS_LB_JSON"
        } | awk 'NF && !seen[$0]++'
      )
    fi
  fi
  if [[ "$lb_status" == "ok" ]]; then
    local -a self_heal_profiles=()
    while IFS= read -r rescue_profile; do
      [[ -n "$rescue_profile" ]] || continue
      self_heal_profiles+=("$rescue_profile")
    done < <(
      near_supply_self_heal_candidates_from_lb_json "$HARNESS_LB_JSON" | awk 'NF && !seen[$0]++'
    )
    if [[ "${#self_heal_profiles[@]}" -gt 0 ]]; then
      if run_near_supply_self_heal "${self_heal_profiles[@]}"; then
        local heal_json=""
        set +e
        heal_json="$(select_load_balancer_json "$mode" "${args[@]}")"
        lb_rc=$?
        set -e
        if [[ "$lb_rc" -eq 0 && -n "$heal_json" ]]; then
          HARNESS_LB_JSON="$heal_json"
          lb_status="$(jq -r '.status' <<<"$HARNESS_LB_JSON")"
        fi
      fi
    fi
  fi
  [[ "$lb_status" == "ok" ]] || die "load balancer could not select a profile: $(jq -r '.reason // .status' <<<"$HARNESS_LB_JSON")"

  HARNESS_LB_LEASE_ID="$(jq -r '.lease_id' <<<"$HARNESS_LB_JSON")"
  HARNESS_LB_PROFILE="$(jq -r '.selected_profile' <<<"$HARNESS_LB_JSON")"
  HARNESS_LB_SELECTION_REASON="$(jq -r '.selection_reason' <<<"$HARNESS_LB_JSON")"
  HARNESS_LB_CONTINUITY_STATUS="$(jq -r '.continuity_status' <<<"$HARNESS_LB_JSON")"
  HARNESS_LB_CONTINUITY_REASON="$(jq -r '.continuity_reason // empty' <<<"$HARNESS_LB_JSON")"

  [[ -n "$HARNESS_LB_PROFILE" && "$HARNESS_LB_PROFILE" != "null" ]] || die "load balancer returned no profile"
  switch_profile "$HARNESS_LB_PROFILE"
  note "load balancer selected $HARNESS_LB_PROFILE ($HARNESS_LB_SELECTION_REASON; $HARNESS_LB_CONTINUITY_STATUS)"
}

auth_context_rebind_resume_allowed() {
  [[ "${HARNESS_LB_CONTINUITY_STATUS:-}" == "cold-required" ]] || return 1
  [[ "${HARNESS_LB_CONTINUITY_REASON:-}" == "auth_context_mismatch_requires_fresh_session" ]] || return 1
  [[ -n "${HARNESS_LB_JSON:-}" ]] || return 1

  local same_account same_user same_org selected_profile bound_profile
  same_account="$(
    jq -r '
      .continuity_handles as $h
      | ($h.bound_account_id != null and $h.selected_account_id != null and $h.bound_account_id == $h.selected_account_id)
    ' <<<"$HARNESS_LB_JSON" 2>/dev/null || printf 'false'
  )"
  same_user="$(
    jq -r '
      .continuity_handles as $h
      | ($h.bound_user_id != null and $h.selected_user_id != null and $h.bound_user_id == $h.selected_user_id)
    ' <<<"$HARNESS_LB_JSON" 2>/dev/null || printf 'false'
  )"
  same_org="$(
    jq -r '
      .continuity_handles as $h
      | ($h.bound_default_org_id != null and $h.selected_default_org_id != null and $h.bound_default_org_id == $h.selected_default_org_id)
    ' <<<"$HARNESS_LB_JSON" 2>/dev/null || printf 'false'
  )"
  selected_profile="$(jq -r '.selected_profile // empty' <<<"$HARNESS_LB_JSON" 2>/dev/null || true)"
  bound_profile="$(jq -r '.bound_profile // empty' <<<"$HARNESS_LB_JSON" 2>/dev/null || true)"

  if [[ "${HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME:-0}" -eq 1 ]]; then
    [[ "$same_account" == "true" && "$same_user" == "true" && "$same_org" == "true" ]]
    return
  fi

  [[ "$same_account" == "true" && "$same_user" == "true" && "$same_org" == "true" ]] || return 1
  [[ -n "$selected_profile" && "$selected_profile" == "$bound_profile" ]]
}

complete_load_balancer_lease() {
  local session_id="${1:-}"
  local exit_code="${2:-0}"
  [[ -n "${HARNESS_LB_LEASE_ID:-}" ]] || return 0

  local -a args
  args=(complete --lease-id "$HARNESS_LB_LEASE_ID" --exit-code "$exit_code")
  if [[ -n "$session_id" ]]; then
    args+=(--session-id "$session_id")
  fi
  load_balancer_json "${args[@]}" >/dev/null || true
  unset HARNESS_LB_LEASE_ID HARNESS_LB_PROFILE HARNESS_LB_SELECTION_REASON HARNESS_LB_CONTINUITY_STATUS HARNESS_LB_CONTINUITY_REASON HARNESS_LB_JSON
}

latest_session_id_or_empty() {
  refresh_session_index
  jq -r 'if length == 0 then empty else (max_by(.last_activity_ts // 0) | .session_id // empty) end' "$SESSION_INDEX_JSON" | awk 'NF { print; exit }'
}

start_new_session() {
  local requested_profile="${1:-}"
  local extra_prompt="${2:-}"
  local opening_text
  opening_text="$(compose_opening_prompt "$extra_prompt")"
  local before_session
  before_session="$(latest_session_id_or_empty || true)"
  local consumer_id="interactive-new:$$:$(date +%s)"
  record_reachability_contact "new-session" "$requested_profile" ""
  select_load_balanced_profile "new" "" "$requested_profile" "$consumer_id"
  note "starting new Overseer session in $WORKSPACE"
  set +e
  run_with_turn_notifier "" launch_codex "" "$opening_text"
  local rc=$?
  set -e
  local after_session
  after_session="$(latest_session_id_or_empty || true)"
  if [[ -n "$after_session" && "$after_session" != "$before_session" ]]; then
    remember_session "$after_session"
    complete_load_balancer_lease "$after_session" "$rc"
  else
    complete_load_balancer_lease "" "$rc"
  fi
  return "$rc"
}

start_interactive_session() {
  local requested_profile="${1:-}"
  local before_session
  before_session="$(latest_session_id_or_empty || true)"
  local consumer_id="interactive-raw:$$:$(date +%s)"
  record_reachability_contact "interactive-session" "$requested_profile" ""
  select_load_balanced_profile "interactive" "" "$requested_profile" "$consumer_id"
  note "starting raw interactive Overseer session in $WORKSPACE"
  set +e
  run_with_turn_notifier "" launch_codex ""
  local rc=$?
  set -e
  local after_session
  after_session="$(latest_session_id_or_empty || true)"
  if [[ -n "$after_session" && "$after_session" != "$before_session" ]]; then
    remember_session "$after_session"
    complete_load_balancer_lease "$after_session" "$rc"
  else
    complete_load_balancer_lease "" "$rc"
  fi
  return "$rc"
}

run_one_shot() {
  local prompt="${1:-}"
  [[ -n "$prompt" ]] || die "one-shot prompt is required"
  note "running one-shot prompt"
  record_reachability_contact "one-shot" "" ""
  launch_codex "exec" "$prompt"
}

session_index_args() {
  local scope
  IFS=':' read -r -a scope <<< "$SESSION_SCOPE_DIRS"

  printf '%s\0' \
    "--sessions-root" "$CODEX_HOME/sessions" \
    "--history" "$CODEX_HOME/history.jsonl" \
    "--workspace" "$WORKSPACE"

  local item
  for item in "${scope[@]}"; do
    [[ -n "$item" ]] || continue
    printf '%s\0' "--scope-dir" "$item"
  done
}

refresh_session_index() {
  local -a args
  while IFS= read -r -d '' token; do
    args+=("$token")
  done < <(session_index_args)

  "$SESSION_INDEX_BIN" "${args[@]}" > "$SESSION_INDEX_JSON"
}

session_query_json() {
  local selector="$1"
  refresh_session_index
  jq "$selector" "$SESSION_INDEX_JSON"
}

latest_session_id() {
  local mode="${1:-scoped}"
  local selector

  if [[ "$mode" == "all" ]]; then
    selector='.[0].session_id // empty'
  else
    selector='([.[] | select(.in_scope)] | if length > 0 then .[0].session_id else empty end), (.[0].session_id // empty)'
  fi

  local result
  result="$(refresh_session_index; jq -r "$selector" "$SESSION_INDEX_JSON" | awk 'NF { print; exit }')"
  [[ -n "$result" ]] || die "no recorded sessions found"
  printf '%s\n' "$result"
}

resolve_session_ref() {
  local ref="${1:-}"

  if [[ -z "$ref" ]]; then
    latest_session_id "scoped"
    return
  fi

  refresh_session_index

  local exact
  exact="$(jq -r --arg ref "$ref" '.[] | select(.session_id == $ref) | .session_id' "$SESSION_INDEX_JSON" | head -n 1)"
  if [[ -n "$exact" ]]; then
    printf '%s\n' "$exact"
    return
  fi

  local matches
  matches="$(jq -r --arg ref "$ref" '.[] | select(.session_id | startswith($ref)) | .session_id' "$SESSION_INDEX_JSON")"
  local count
  count="$(printf '%s\n' "$matches" | awk 'NF { count += 1 } END { print count + 0 }')"
  if [[ "$count" -eq 1 ]]; then
    printf '%s\n' "$matches"
    return
  fi

  if [[ "$count" -gt 1 ]]; then
    die "session id prefix is ambiguous: $ref"
  fi

  die "session not found locally: $ref"
}

picker_rows() {
  local mode="${1:-scoped}"
  refresh_session_index

  if [[ "$mode" == "all" ]]; then
    jq -r '.[] | [.session_id, .last_activity_iso, .scope_label, .cwd, .last_text] | @tsv' "$SESSION_INDEX_JSON"
    return
  fi

  if jq -e 'any(.[]; .in_scope)' "$SESSION_INDEX_JSON" >/dev/null; then
    jq -r '.[] | select(.in_scope) | [.session_id, .last_activity_iso, .scope_label, .cwd, .last_text] | @tsv' "$SESSION_INDEX_JSON"
  else
    jq -r '.[] | [.session_id, .last_activity_iso, .scope_label, .cwd, .last_text] | @tsv' "$SESSION_INDEX_JSON"
  fi
}

pick_session_id() {
  local mode="${1:-scoped}"
  local rows
  rows="$(picker_rows "$mode")"
  [[ -n "$rows" ]] || die "no sessions available to pick"

  if [[ -x "$FZF_BIN" && ( "$HARNESS_FORCE_FZF" -eq 1 || ( -t 0 && -t 1 ) ) ]]; then
    local selected
    selected="$(printf '%s\n' "$rows" | "$FZF_BIN" --delimiter=$'\t' --with-nth=2.. --no-sort --prompt='overseer session> ')"
    [[ -n "$selected" ]] || die "session selection aborted"
    printf '%s\n' "$selected" | cut -f 1
    return
  fi

  local -a lines
  mapfile -t lines < <(printf '%s\n' "$rows")
  local i=1
  local line
  for line in "${lines[@]}"; do
    IFS=$'\t' read -r session_id last_activity scope_label cwd last_text <<< "$line"
    printf '%2d) %s  %s  %s  %s\n' "$i" "$last_activity" "$scope_label" "$cwd" "$last_text" >&2
    i=$((i + 1))
  done

  local selection
  read -r -p "Pick session [1-${#lines[@]}]: " selection
  [[ "$selection" =~ ^[0-9]+$ ]] || die "selection must be numeric"
  (( selection >= 1 && selection <= ${#lines[@]} )) || die "selection out of range"
  printf '%s\n' "${lines[$((selection - 1))]}" | cut -f 1
}

remember_session() {
  local session_id="$1"
  ensure_state_dir
  printf '%s\n' "$session_id" > "$STATE_DIR/last-session-id"
}

start_fresh_session_for_cold_required_resume() {
  local previous_session_id="$1"
  local prompt="${2:-}"
  local requested_profile="${3:-}"
  local continuity_reason="${HARNESS_LB_CONTINUITY_REASON:-cold_required}"

  local opening_text
  opening_text="$(compose_cold_required_resume_prompt "$previous_session_id" "$continuity_reason" "$prompt")"
  local before_session
  before_session="$(latest_session_id_or_empty || true)"
  note "load balancer requires a fresh session for $previous_session_id ($continuity_reason); starting a new session on $HARNESS_LB_PROFILE"
  note "requested resume of $previous_session_id was demoted to a fresh session; do not assume old-session continuity"
  set +e
  run_with_turn_notifier "" launch_codex "" "$opening_text"
  local rc=$?
  set -e
  local after_session
  after_session="$(latest_session_id_or_empty || true)"
  if [[ -n "$after_session" && "$after_session" != "$before_session" ]]; then
    record_reachability_contact "fresh-session-after-cold-required-resume" "$requested_profile" "$after_session"
    remember_session "$after_session"
    complete_load_balancer_lease "$after_session" "$rc"
  else
    complete_load_balancer_lease "" "$rc"
  fi
  return "$rc"
}

resume_session() {
  local session_ref="${1:-}"
  local prompt="${2:-}"
  local requested_profile="${3:-}"
  local session_id
  session_id="$(resolve_session_ref "$session_ref")"
  record_reachability_contact "resume-session" "$requested_profile" "$session_id"
  select_load_balanced_profile "resume" "$session_id" "$requested_profile" "interactive-session:$session_id"
  if [[ "${HARNESS_LB_CONTINUITY_STATUS:-}" == "cold-required" ]]; then
    if auth_context_rebind_resume_allowed; then
      if [[ "${HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME:-0}" -eq 1 ]]; then
        note "overriding cold-required auth-context mismatch for $session_id; attempting direct resume on $HARNESS_LB_PROFILE"
      else
        note "auto-rebinding repaired auth context for $session_id on $HARNESS_LB_PROFILE; attempting direct resume"
      fi
    else
      start_fresh_session_for_cold_required_resume "$session_id" "$prompt" "$requested_profile"
      return "$?"
    fi
  fi
  guard_against_duplicate_local_resume "$session_id"
  remember_session "$session_id"
  note "resuming session $session_id"

  if [[ -n "$prompt" ]]; then
    set +e
    run_with_turn_notifier "$session_id" launch_codex "resume" "$session_id" "$prompt"
    local rc=$?
    set -e
  else
    set +e
    run_with_turn_notifier "$session_id" launch_codex "resume" "$session_id"
    local rc=$?
    set -e
  fi
  complete_load_balancer_lease "$session_id" "$rc"
  return "$rc"
}
