#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOUSAGE'
usage: launch-chromium-profile.sh PROFILE_NAME [options] [url-or-extra-chromium-args...]

options:
  --remote-debugging-port PORT|auto   expose a DevTools port and record the request in profile metadata
  --headless                          add --headless=new
  --skip-extension                    do not load the GlassTTY unpacked extension
  --skip-native-host-audit            do not snapshot browser-aware native-host state into the profile directory before launch
  --                                  stop option parsing and forward the remaining Chromium args verbatim
EOUSAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

PROFILE_NAME="$1"
shift || true

GLASSTTY_HOME="${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$GLASSTTY_HOME/profiles/$PROFILE_NAME"
EXT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/extension"
PYTHON_BIN="${PYTHON:-python3}"
if [[ -n "${GLASSTTY_CHROMIUM_BIN:-}" ]]; then
  CHROMIUM_BIN="$GLASSTTY_CHROMIUM_BIN"
elif [[ -n "${CHROMIUM_BIN:-}" ]]; then
  CHROMIUM_BIN="$CHROMIUM_BIN"
else
  CHROMIUM_BIN="$($PYTHON_BIN "$SCRIPT_DIR/chrome-for-testing.py" local-executable 2>/dev/null || true)"
  if [[ -z "$CHROMIUM_BIN" ]]; then
    CHROMIUM_BIN="chromium"
  fi
fi

EXTRA_ARGS=()
LOAD_EXTENSION=1
SNAPSHOT_NATIVE_HOST_AUDIT=1
REMOTE_DEBUGGING_MODE=""
REMOTE_DEBUGGING_PORT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote-debugging-port)
      [[ $# -ge 2 ]] || { echo "missing value for --remote-debugging-port" >&2; exit 1; }
      value="$2"
      shift 2
      ;;
    --remote-debugging-port=*)
      value="${1#*=}"
      shift
      ;;
    --headless)
      EXTRA_ARGS+=("--headless=new")
      shift
      continue
      ;;
    --skip-extension)
      LOAD_EXTENSION=0
      shift
      continue
      ;;
    --skip-native-host-audit)
      SNAPSHOT_NATIVE_HOST_AUDIT=0
      shift
      continue
      ;;
    --)
      shift
      EXTRA_ARGS+=("$@")
      break
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      continue
      ;;
  esac

  if [[ "$value" == "auto" ]]; then
    REMOTE_DEBUGGING_MODE="ephemeral"
    REMOTE_DEBUGGING_PORT="0"
  else
    REMOTE_DEBUGGING_MODE="fixed"
    REMOTE_DEBUGGING_PORT="$value"
  fi
  EXTRA_ARGS+=("--remote-debugging-port=$REMOTE_DEBUGGING_PORT")
done

mkdir -p "$PROFILE_DIR"

if [[ $SNAPSHOT_NATIVE_HOST_AUDIT -eq 1 ]]; then
  "$PYTHON_BIN" "$SCRIPT_DIR/native-host-report.py" --browser-bin "$CHROMIUM_BIN" --host-exe "$SCRIPT_DIR/native-host-wrapper.sh" --pretty > "$PROFILE_DIR/glasstty-native-host.json"
fi

record_args=("$SCRIPT_DIR/profile-report.py" record-launch --profile-dir "$PROFILE_DIR" --profile-name "$PROFILE_NAME" --chromium-bin "$CHROMIUM_BIN")
if [[ $LOAD_EXTENSION -eq 1 ]]; then
  record_args+=(--extension-loaded --extension-dir "$EXT_DIR")
fi
if [[ -n "$REMOTE_DEBUGGING_MODE" ]]; then
  record_args+=(--remote-debugging-mode "$REMOTE_DEBUGGING_MODE" --remote-debugging-port "$REMOTE_DEBUGGING_PORT")
fi
for arg in "${EXTRA_ARGS[@]}"; do
  record_args+=("--arg=$arg")
done
"$PYTHON_BIN" "${record_args[@]}" >/dev/null

CMD=("$CHROMIUM_BIN" "--user-data-dir=$PROFILE_DIR")
if [[ $LOAD_EXTENSION -eq 1 ]]; then
  CMD+=("--disable-extensions-except=$EXT_DIR" "--load-extension=$EXT_DIR")
fi
CMD+=("${EXTRA_ARGS[@]}")
exec "${CMD[@]}"
