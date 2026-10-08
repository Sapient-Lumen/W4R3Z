#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: install-native-host.sh [--target auto|playwright|combined|chromium|chrome|chrome-for-testing|DIR] [--all-recommended] [--os linux|macos] [--extension-id ID|auto] [--host-exe ABS_PATH]

Examples:
  ./scripts/install-native-host.sh --target auto --extension-id auto
  ./scripts/install-native-host.sh --target playwright --extension-id auto
  ./scripts/install-native-host.sh --target combined --extension-id auto
  ./scripts/install-native-host.sh --target chrome-for-testing --extension-id auto
  ./scripts/install-native-host.sh --target auto --all-recommended --extension-id auto
  ./scripts/install-native-host.sh --target chromium --extension-id abcdefghijklmnopqrstuvwxyzabcdef --host-exe "$PWD/scripts/native-host-wrapper.sh"
USAGE
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
PYTHON_BIN="${PYTHON:-python3}"
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
  EXTENSION_ID="$("$PYTHON_BIN" "$SCRIPT_DIR/scripts/extension-id.py" "$SCRIPT_DIR/extension/manifest.json")"
fi

if [[ "$ALL_RECOMMENDED" == "1" && ( "$TARGET" == *"/"* || "$TARGET" == .* || "$TARGET" == ~* ) ]]; then
  echo "--all-recommended cannot be combined with an explicit directory target" >&2
  exit 1
fi

RESOLVE_ARGS=("$PYTHON_BIN" "$SCRIPT_DIR/scripts/native-host-report.py" resolve-targets --target "$TARGET" --print-targets)
if [[ "$ALL_RECOMMENDED" == "1" ]]; then
  RESOLVE_ARGS+=(--all-recommended)
fi
mapfile -t INSTALL_TARGETS < <("${RESOLVE_ARGS[@]}")
if [[ "${#INSTALL_TARGETS[@]}" -eq 0 ]]; then
  echo "failed to resolve native-host install target(s)" >&2
  exit 1
fi

for RESOLVED_TARGET in "${INSTALL_TARGETS[@]}"; do
  TARGET_DIR="$($PYTHON_BIN - "$SCRIPT_DIR/scripts" "$RESOLVED_TARGET" "$OS_NAME" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from native_host_manifest import resolve_target_dir
print(resolve_target_dir(sys.argv[2], sys.argv[3]))
PY
)"
  mkdir -p "$TARGET_DIR"
  OUT="$TARGET_DIR/com.glasstty.bridge.json"
  "$PYTHON_BIN" - "$SCRIPT_DIR/scripts" "$OUT" "$HOST_EXE" "$EXTENSION_ID" <<'PY'
import json
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from native_host_manifest import render_manifest
out = Path(sys.argv[2])
payload = render_manifest(host_path=sys.argv[3], extension_id=sys.argv[4])
out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
PY
  chmod 0644 "$OUT"
  echo "wrote $OUT for extension $EXTENSION_ID using host $HOST_EXE"
done
