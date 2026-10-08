#!/usr/bin/env bash
set -euo pipefail

GLASSTTY_HOME="${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
PROFILE_ROOT="$GLASSTTY_HOME/profiles"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$PROFILE_ROOT"

usage() {
  cat >&2 <<'EOUSAGE'
usage:
  glasstty-profile.sh list
  glasstty-profile.sh path PROFILE_NAME
  glasstty-profile.sh info PROFILE_NAME
  glasstty-profile.sh open PROFILE_NAME [launch options or chromium args...]

examples:
  glasstty-profile.sh open chatgpt --remote-debugging-port auto https://chatgpt.com/
  glasstty-profile.sh info chatgpt
EOUSAGE
}

cmd="${1:-}"
case "$cmd" in
  list)
    find "$PROFILE_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort || true
    ;;
  path)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    echo "$PROFILE_ROOT/$2"
    ;;
  info)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    profile="$2"
    info_path="$PROFILE_ROOT/$profile/profile-launch.json"
    native_path="$PROFILE_ROOT/$profile/glasstty-native-host.json"
    python - "$info_path" "$native_path" <<'PY'
import json
import sys
from pathlib import Path
info_path = Path(sys.argv[1])
native_path = Path(sys.argv[2])
payload = {
    'profile_launch_path': str(info_path),
    'profile_launch': json.loads(info_path.read_text(encoding='utf-8')) if info_path.exists() else None,
    'native_host_report_path': str(native_path),
    'native_host_report_exists': native_path.exists(),
}
print(json.dumps(payload, indent=2))
PY
    ;;
  open)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec "$SCRIPT_DIR/launch-chromium-profile.sh" "$profile" "$@"
    ;;
  -h|--help|*)
    usage
    [[ "$cmd" == "-h" || "$cmd" == "--help" ]] && exit 0 || exit 1
    ;;
esac
