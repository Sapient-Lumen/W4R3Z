#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/home/overseer/.human/scripts/overseer-harness-lib.sh
source "$SCRIPT_DIR/scripts/overseer-harness-lib.sh"

reexec_as_overseer "$0" "$@"

profile=""
interactive=0
prompt=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      shift
      profile="${1:-}"
      [[ -n "$profile" ]] || die "--profile requires a value"
      ;;
    --interactive)
      interactive=1
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
  shift
done

if [[ $# -gt 0 ]]; then
  prompt="$*"
fi

ensure_state_dir
ensure_codex_config_defaults
check_launch_deps

if [[ "$interactive" -eq 1 ]]; then
  start_interactive_session "$profile"
else
  start_new_session "$profile" "$prompt"
fi
