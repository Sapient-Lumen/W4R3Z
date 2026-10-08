#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 PROFILE_NAME [extra chromium args...]" >&2
  exit 1
fi

PROFILE_NAME="$1"
shift || true

GLASSTTY_HOME="${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
PROFILE_DIR="$GLASSTTY_HOME/profiles/$PROFILE_NAME"
EXT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/extension"
CHROMIUM_BIN="${CHROMIUM_BIN:-chromium}"

mkdir -p "$PROFILE_DIR"

exec "$CHROMIUM_BIN"   --user-data-dir="$PROFILE_DIR"   --disable-extensions-except="$EXT_DIR"   --load-extension="$EXT_DIR"   "$@"
