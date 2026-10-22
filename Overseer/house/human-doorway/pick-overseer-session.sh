#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/home/overseer/.human/scripts/overseer-harness-lib.sh
source "$SCRIPT_DIR/scripts/overseer-harness-lib.sh"

reexec_as_overseer "$0" "$@"

profile=""
mode="scoped"
resume_prompt=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      shift
      profile="${1:-}"
      [[ -n "$profile" ]] || die "--profile requires a value"
      ;;
    --all)
      mode="all"
      ;;
    --prompt)
      shift
      resume_prompt="${1:-}"
      [[ -n "$resume_prompt" ]] || die "--prompt requires a value"
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
  if [[ -n "$resume_prompt" ]]; then
    resume_prompt="$resume_prompt $*"
  else
    resume_prompt="$*"
  fi
fi

ensure_state_dir
ensure_codex_config_defaults
check_launch_deps

selected_session="$(pick_session_id "$mode")"
resume_session "$selected_session" "$resume_prompt" "$profile"
