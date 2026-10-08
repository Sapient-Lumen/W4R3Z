#!/usr/bin/env bash
set -euo pipefail

GLASSTTY_HOME="${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
PROFILE_ROOT="$GLASSTTY_HOME/profiles"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$PROFILE_ROOT"

usage() {
  cat >&2 <<'EOF'
usage:
  glasstty-profile.sh list
  glasstty-profile.sh triage [--pretty]
  glasstty-profile.sh fleet-capture [--output-dir DIR] [--pretty]
  glasstty-profile.sh fleet-captures [--pretty]
  glasstty-profile.sh path PROFILE_NAME
  glasstty-profile.sh info PROFILE_NAME [--pretty]
  glasstty-profile.sh open PROFILE_NAME [launch options or chromium args...]
  glasstty-profile.sh reopen PROFILE_NAME [reopen options...]
  glasstty-profile.sh resume-proof PROFILE_NAME [mv3-worker-resume options...]
  glasstty-profile.sh capture PROFILE_NAME [capture options...]
  glasstty-profile.sh captures PROFILE_NAME [--pretty]

examples:
  glasstty-profile.sh open main chrome://extensions/
  glasstty-profile.sh open lab --remote-debugging-port auto http://127.0.0.1:8765/
  glasstty-profile.sh info main --pretty
  glasstty-profile.sh triage --pretty
  glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture
  glasstty-profile.sh fleet-captures --pretty
  glasstty-profile.sh reopen lab --remote-debugging-port auto
  glasstty-profile.sh reopen lab --allow-discovered-browser-fallback --remote-debugging-port auto
  glasstty-profile.sh resume-proof lab --output validation/latest/mv3-worker-resume-lab.json --timeout 25
  glasstty-profile.sh capture lab --output-dir validation/latest/profile-capture-lab
  glasstty-profile.sh captures lab --pretty
EOF
}

cmd="${1:-}"
case "$cmd" in
  list)
    find "$PROFILE_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f
' | sort || true
    ;;
  triage)
    shift 1
    exec python "$SCRIPT_DIR/profile-report.py" triage "$@"
    ;;
  fleet-capture)
    shift 1
    exec python "$SCRIPT_DIR/profile-fleet-capture.py" "$@"
    ;;
  fleet-captures)
    shift 1
    exec python "$SCRIPT_DIR/profile-fleet-capture.py" --history-only "$@"
    ;;
  path)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    echo "$PROFILE_ROOT/$2"
    ;;
  info)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec python "$SCRIPT_DIR/profile-report.py" --profile "$profile" "$@"
    ;;
  open)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec "$SCRIPT_DIR/launch-chromium-profile.sh" "$profile" "$@"
    ;;
  reopen)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec python "$SCRIPT_DIR/reopen-profile.py" "$profile" "$@"
    ;;
  resume-proof)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec python "$SCRIPT_DIR/mv3-worker-resume.py" --profile "$profile" "$@"
    ;;
  capture)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec python "$SCRIPT_DIR/profile-capture.py" "$profile" "$@"
    ;;
  captures)
    [[ $# -ge 2 ]] || { usage; exit 1; }
    profile="$2"
    shift 2
    exec python "$SCRIPT_DIR/profile-capture.py" "$profile" --history-only "$@"
    ;;
  *)
    usage
    exit 1
    ;;
esac
