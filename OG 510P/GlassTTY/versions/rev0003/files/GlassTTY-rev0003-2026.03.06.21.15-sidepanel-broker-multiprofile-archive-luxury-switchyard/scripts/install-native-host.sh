#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: install-native-host.sh [--target chromium|chrome|chrome-for-testing|DIR] --extension-id ID --host-exe CMD

Examples:
  ./scripts/install-native-host.sh     --target chromium     --extension-id abcdefghijklmnopqrstuvwxyzabcdef     --host-exe "$PWD/daemon/.venv/bin/python -m glassttyd.native_host"

  ./scripts/install-native-host.sh     --target "$HOME/.config/chromium/NativeMessagingHosts"     --extension-id abcdefghijklmnopqrstuvwxyzabcdef     --host-exe "$PWD/daemon/.venv/bin/python -m glassttyd.native_host"
EOF
}

TARGET="chromium"
EXTENSION_ID=""
HOST_EXE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="$2"
      shift 2
      ;;
    --extension-id)
      EXTENSION_ID="$2"
      shift 2
      ;;
    --host-exe)
      HOST_EXE="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$EXTENSION_ID" || -z "$HOST_EXE" ]]; then
  usage
  exit 1
fi

case "$TARGET" in
  chromium) TARGET_DIR="$HOME/.config/chromium/NativeMessagingHosts" ;;
  chrome) TARGET_DIR="$HOME/.config/google-chrome/NativeMessagingHosts" ;;
  chrome-for-testing) TARGET_DIR="$HOME/.config/google-chrome-for-testing/NativeMessagingHosts" ;;
  *) TARGET_DIR="$TARGET" ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$SCRIPT_DIR/native-host/com.glasstty.bridge.template.json"
OUT="$TARGET_DIR/com.glasstty.bridge.json"

mkdir -p "$TARGET_DIR"

sed   -e "s|__HOST_PATH__|$HOST_EXE|g"   -e "s|__EXTENSION_ID__|$EXTENSION_ID|g"   "$TEMPLATE" > "$OUT"

chmod 0644 "$OUT"
echo "wrote $OUT"
