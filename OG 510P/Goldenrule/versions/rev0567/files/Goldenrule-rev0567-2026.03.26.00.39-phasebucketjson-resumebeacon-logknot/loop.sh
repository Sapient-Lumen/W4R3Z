#!/usr/bin/env bash
set -euo pipefail

# Always-YOLO loop template (edit queue logic by hand).
# Runs wrappers inside sandworm: .yolo/bin/{codex-yolo,gemini-yolo,claude-yolo}

find_root() {
  local d="$(pwd -P)"
  while [[ "$d" != "/" && ! -d "$d/.sandworm" ]]; do d="$(dirname "$d")"; done
  [[ -d "$d/.sandworm" ]] || { echo "ERROR: no .sandworm/ found above $(pwd -P)" >&2; exit 1; }
  echo "$d"
}

ROOT="$(find_root)"
SW="${SW:-sandworm}"
PROVIDER="${PROVIDER:-codex}"  # codex|claude|gemini

# Load model defaults
[[ -f "$ROOT/.yolo/models.env" ]] && source "$ROOT/.yolo/models.env"

CODEX="$ROOT/.yolo/bin/codex-yolo"
GEMINI="$ROOT/.yolo/bin/gemini-yolo"
CLAUDE="$ROOT/.yolo/bin/claude-yolo"

run_fresh() {
  local prompt="$1"
  case "$PROVIDER" in
    codex)  "$SW" run -- "$CODEX" "$prompt" ;;
    gemini) "$SW" run -- "$GEMINI" "$prompt" ;;
    claude) "$SW" run -- "$CLAUDE" "$prompt" ;;
    *) echo "ERROR: unknown PROVIDER=$PROVIDER" >&2; exit 2 ;;
  esac
}

run_resume() {
  local prompt="$1"
  case "$PROVIDER" in
    codex)  "$SW" run -- "$CODEX"  --resume-last "$prompt" ;;
    gemini) "$SW" run -- "$GEMINI" --resume-last "$prompt" ;;
    claude) "$SW" run -- "$CLAUDE" --resume-last "$prompt" ;;
    *) echo "ERROR: unknown PROVIDER=$PROVIDER" >&2; exit 2 ;;
  esac
}

INTRO_PROMPT=$'You are in a sandworm container and have full autonomy.\nKeep changes small and test when relevant.'
STEP_PROMPT=$'Continue the work. Choose the next smallest useful action and do it.'

# Hand-edit your queue right here:
QUEUE=(
  # "Task: ..."
)

STEPS=5

echo "ROOT=$ROOT"
echo "PROVIDER=$PROVIDER"
echo "CODEX_MODEL=${CODEX_MODEL:-}"
echo "GEMINI_MODEL=${GEMINI_MODEL:-}"
echo

run_fresh "$INTRO_PROMPT"

# Pattern A: fixed step loop
for ((i=1; i<=STEPS; i++)); do
  echo "---- step $i/$STEPS ----"
  run_resume "$STEP_PROMPT"
done

# Pattern B: queue
# for task in "${QUEUE[@]}"; do
#   run_resume "$task"
# done
