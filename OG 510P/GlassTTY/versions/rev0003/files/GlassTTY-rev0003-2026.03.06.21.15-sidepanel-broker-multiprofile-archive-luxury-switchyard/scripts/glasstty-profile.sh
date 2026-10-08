#!/usr/bin/env bash
set -euo pipefail

GLASSTTY_HOME="${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
PROFILE_ROOT="$GLASSTTY_HOME/profiles"
mkdir -p "$PROFILE_ROOT"

usage() {
  cat >&2 <<'EOF'
usage:
  glasstty-profile.sh list
  glasstty-profile.sh path PROFILE_NAME
  glasstty-profile.sh open PROFILE_NAME [url-or-extra-chromium-args...]
EOF
}

cmd="${1:-}"
case "$cmd" in
  list)
    find "$PROFILE_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f
' | sort || true
    ;;
  path)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    echo "$PROFILE_ROOT/$2"
    ;;
  open)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/launch-chromium-profile.sh" "$profile" "$@"
    ;;
  *)
    usage
    exit 1
    ;;
esac
