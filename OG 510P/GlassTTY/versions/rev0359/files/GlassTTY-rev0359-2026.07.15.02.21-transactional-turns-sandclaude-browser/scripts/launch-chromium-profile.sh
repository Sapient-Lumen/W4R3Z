#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOUSAGE'
usage: launch-chromium-profile.sh PROFILE_NAME [options] [url-or-extra-chromium-args...]

options:
  --remote-debugging-port PORT|auto   expose a DevTools port; auto asks Chromium for an ephemeral port
  --headless                          add --headless=new
  --skip-extension                    do not load the GlassTTY unpacked extension
  --skip-native-host-audit            do not snapshot browser-aware native-host state into the profile directory before launch
  --                                  stop option parsing and forward the remaining Chromium args verbatim

Environment:
  GLASSTTY_HOME          default: $HOME/.local/share/glasstty
  GLASSTTY_CHROMIUM_BIN  preferred Chromium-family executable
  CHROMIUM_BIN           fallback Chromium-family executable
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
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_DIR="$GLASSTTY_HOME/profiles/$PROFILE_NAME"
EXT_DIR="$ROOT/extension"
PYTHON_BIN="${PYTHON:-python3}"

if [[ -n "${GLASSTTY_CHROMIUM_BIN:-}" ]]; then
  CHROMIUM_BIN="$GLASSTTY_CHROMIUM_BIN"
elif [[ -n "${CHROMIUM_BIN:-}" ]]; then
  CHROMIUM_BIN="$CHROMIUM_BIN"
else
  CHROMIUM_BIN="$($PYTHON_BIN - "$SCRIPT_DIR" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from browser_binaries import discover_browser_executable
print(discover_browser_executable().get('path') or 'chromium')
PY
)"
fi

EXTRA_ARGS=()
LOAD_EXTENSION=1
SNAPSHOT_NATIVE_HOST_AUDIT=1
REMOTE_DEBUGGING_MODE="off"
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
    -h|--help)
      usage
      exit 0
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
  elif [[ "$value" == "off" || -z "$value" ]]; then
    REMOTE_DEBUGGING_MODE="off"
    REMOTE_DEBUGGING_PORT=""
  else
    REMOTE_DEBUGGING_MODE="fixed"
    REMOTE_DEBUGGING_PORT="$value"
  fi
  if [[ -n "$REMOTE_DEBUGGING_PORT" ]]; then
    EXTRA_ARGS+=("--remote-debugging-port=$REMOTE_DEBUGGING_PORT")
  fi
done

mkdir -p "$PROFILE_DIR"

if [[ $SNAPSHOT_NATIVE_HOST_AUDIT -eq 1 ]]; then
  GLASSTTY_BROWSER_BIN="$CHROMIUM_BIN" "$PYTHON_BIN" "$SCRIPT_DIR/native-host-report.py" \
    --browser-bin "$CHROMIUM_BIN" \
    --host-exe "$SCRIPT_DIR/native-host-wrapper.sh" \
    --pretty > "$PROFILE_DIR/glasstty-native-host.json" || true
fi

"$PYTHON_BIN" - "$PROFILE_DIR/profile-launch.json" "$PROFILE_NAME" "$PROFILE_DIR" "$CHROMIUM_BIN" "$EXT_DIR" "$LOAD_EXTENSION" "$REMOTE_DEBUGGING_MODE" "$REMOTE_DEBUGGING_PORT" "${EXTRA_ARGS[@]}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
out = Path(sys.argv[1])
profile_name, profile_dir, chromium_bin, extension_dir = sys.argv[2:6]
load_extension = sys.argv[6] == '1'
remote_mode = sys.argv[7]
remote_port = sys.argv[8] or None
args = sys.argv[9:]
payload = {
    'schema_version': 1,
    'profile_name': profile_name,
    'profile_dir': profile_dir,
    'chromium_bin': chromium_bin,
    'extension_loaded': load_extension,
    'extension_dir': extension_dir if load_extension else None,
    'remote_debugging_mode': remote_mode,
    'remote_debugging_port': remote_port,
    'args': args,
    'launched_at': datetime.now(timezone.utc).isoformat(),
}
out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
PY

CMD=("$CHROMIUM_BIN" "--user-data-dir=$PROFILE_DIR")
if [[ $LOAD_EXTENSION -eq 1 ]]; then
  CMD+=("--disable-extensions-except=$EXT_DIR" "--load-extension=$EXT_DIR")
fi
CMD+=("${EXTRA_ARGS[@]}")
exec "${CMD[@]}"
