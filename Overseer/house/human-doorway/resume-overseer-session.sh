#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/home/overseer/.human/scripts/overseer-harness-lib.sh
source "$SCRIPT_DIR/scripts/overseer-harness-lib.sh"

reexec_as_overseer "$0" "$@"

profile=""
session_ref=""
resume_prompt=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      shift
      profile="${1:-}"
      [[ -n "$profile" ]] || die "--profile requires a value"
      ;;
    --session)
      shift
      session_ref="${1:-}"
      [[ -n "$session_ref" ]] || die "--session requires a value"
      ;;
    --prompt)
      shift
      resume_prompt="${1:-}"
      [[ -n "$resume_prompt" ]] || die "--prompt requires a value"
      ;;
    --allow-auth-rebind-resume)
      HARNESS_ALLOW_AUTH_CONTEXT_REBIND_RESUME=1
      ;;
    --)
      shift
      break
      ;;
    *)
      if [[ -z "$session_ref" ]]; then
        session_ref="$1"
      elif [[ -z "$resume_prompt" ]]; then
        resume_prompt="$1"
      else
        resume_prompt="$resume_prompt $1"
      fi
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

resume_session "$session_ref" "$resume_prompt" "$profile"
