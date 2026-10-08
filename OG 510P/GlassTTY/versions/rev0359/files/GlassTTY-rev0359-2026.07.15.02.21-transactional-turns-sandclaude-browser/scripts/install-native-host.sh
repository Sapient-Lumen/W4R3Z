#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: install-native-host.sh [--target auto|chromium|chrome|chrome-for-testing|DIR] [--all-recommended] [--os linux|macos] [--extension-id ID|auto] [--host-exe ABS_PATH]

Examples:
  ./scripts/install-native-host.sh --target auto --extension-id auto
  ./scripts/install-native-host.sh --target chrome-for-testing --extension-id auto
  ./scripts/install-native-host.sh --target auto --all-recommended --extension-id auto
  ./scripts/install-native-host.sh --target chromium --extension-id abcdefghijklmnopqrstuvwxyzabcdef --host-exe "$PWD/scripts/native-host-wrapper.sh"
USAGE
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

resolve_dir() {
  local target="$1"
  local os_name="$2"
  if [[ "$target" == */* || "$target" == .* || "$target" == ~* ]]; then
    printf '%s\n' "${target/#\~/$HOME}"
    return 0
  fi
  case "$os_name:$target" in
    linux:chromium)
      printf '%s\n' "$HOME/.config/chromium/NativeMessagingHosts" ;;
    linux:chrome)
      printf '%s\n' "$HOME/.config/google-chrome/NativeMessagingHosts" ;;
    linux:chrome-for-testing)
      printf '%s\n' "$HOME/.config/google-chrome-for-testing/NativeMessagingHosts" ;;
    macos:chromium)
      printf '%s\n' "$HOME/Library/Application Support/Chromium/NativeMessagingHosts" ;;
    macos:chrome)
      printf '%s\n' "$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts" ;;
    macos:chrome-for-testing)
      printf '%s\n' "$HOME/Library/Application Support/Google/Chrome for Testing/NativeMessagingHosts" ;;
    *)
      echo "unknown native-host target for $os_name: $target" >&2
      return 1 ;;
  esac
}

TARGET="auto"
OS_NAME=""
EXTENSION_ID="auto"
HOST_EXE=""
ALL_RECOMMENDED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --all-recommended) ALL_RECOMMENDED=1; shift ;;
    --os) OS_NAME="$2"; shift 2 ;;
    --extension-id) EXTENSION_ID="$2"; shift 2 ;;
    --host-exe) HOST_EXE="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$OS_NAME" ]]; then
  case "$(uname -s)" in
    Linux) OS_NAME="linux" ;;
    Darwin) OS_NAME="macos" ;;
    *) echo "unsupported OS; pass --os linux or --os macos explicitly" >&2; exit 1 ;;
  esac
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_SPEC="${PYTHON:-python3}"
# shellcheck disable=SC2206
PYTHON_CMD=( $PYTHON_SPEC )
if [[ -z "$HOST_EXE" ]]; then
  HOST_EXE="$SCRIPT_DIR/scripts/native-host-wrapper.sh"
fi
if [[ ! -e "$HOST_EXE" ]]; then
  echo "host executable not found: $HOST_EXE" >&2
  exit 1
fi
if [[ ! -x "$HOST_EXE" ]]; then
  chmod +x "$HOST_EXE" 2>/dev/null || true
fi
if [[ ! -x "$HOST_EXE" ]]; then
  echo "host executable must exist and be executable: $HOST_EXE" >&2
  exit 1
fi
if [[ "$HOST_EXE" != /* ]]; then
  echo "host executable must be an absolute path: $HOST_EXE" >&2
  exit 1
fi

if [[ "$EXTENSION_ID" == "auto" ]]; then
  EXTENSION_ID="$("${PYTHON_CMD[@]}" "$SCRIPT_DIR/scripts/extension-id.py" "$SCRIPT_DIR/extension/manifest.json")"
fi

if [[ "$ALL_RECOMMENDED" == "1" && ( "$TARGET" == *"/"* || "$TARGET" == .* || "$TARGET" == ~* ) ]]; then
  echo "--all-recommended cannot be combined with an explicit directory target" >&2
  exit 1
fi

INSTALL_TARGETS=()
if [[ "$TARGET" != "auto" && "$TARGET" != "recommended" ]]; then
  INSTALL_TARGETS=("$TARGET")
elif [[ -n "${GLASSTTY_BROWSER_BIN:-}" ]]; then
  BROWSER_LOWER="$(printf '%s' "$GLASSTTY_BROWSER_BIN" | tr '[:upper:]' '[:lower:]')"
  if [[ "$BROWSER_LOWER" == *"chrome-for-testing"* ]]; then
    if [[ "$BROWSER_LOWER" == *"146."* ]]; then
      INSTALL_TARGETS=("chrome-for-testing")
    else
      INSTALL_TARGETS=("chrome")
    fi
  elif [[ "$BROWSER_LOWER" == *"google-chrome"* ]]; then
    INSTALL_TARGETS=("chrome")
  else
    INSTALL_TARGETS=("chromium")
  fi
else
  RESOLVE_ARGS=("${PYTHON_CMD[@]}" "$SCRIPT_DIR/scripts/native-host-report.py" resolve-targets --target "$TARGET" --print-targets)
  if [[ "$ALL_RECOMMENDED" == "1" ]]; then
    RESOLVE_ARGS+=(--all-recommended)
  fi
  mapfile -t INSTALL_TARGETS < <("${RESOLVE_ARGS[@]}")
fi
if [[ "${#INSTALL_TARGETS[@]}" -eq 0 ]]; then
  echo "failed to resolve native-host install target(s)" >&2
  exit 1
fi

ESCAPED_HOST="$(json_escape "$HOST_EXE")"
ESCAPED_EXTENSION_ID="$(json_escape "$EXTENSION_ID")"
for RESOLVED_TARGET in "${INSTALL_TARGETS[@]}"; do
  TARGET_DIR="$(resolve_dir "$RESOLVED_TARGET" "$OS_NAME")"
  mkdir -p "$TARGET_DIR"
  OUT="$TARGET_DIR/com.glasstty.bridge.json"
  cat > "$OUT" <<JSON
{
  "name": "com.glasstty.bridge",
  "description": "GlassTTY native messaging host",
  "path": "$ESCAPED_HOST",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$ESCAPED_EXTENSION_ID/"
  ]
}
JSON
  chmod 0644 "$OUT"
  echo "wrote $OUT for extension $EXTENSION_ID using host $HOST_EXE"
done
