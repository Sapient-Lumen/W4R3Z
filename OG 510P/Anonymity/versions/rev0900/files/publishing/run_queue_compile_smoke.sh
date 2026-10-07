#!/usr/bin/env bash
set -euo pipefail
ROOT="."
WRITE_REPORT=""
LATEX_COMMAND="pdflatex"
TIMEOUT_SECONDS="30"
PASSES="${QUEUE_COMPILE_PASSES:-3}"
JOBS="${QUEUE_COMPILE_JOBS:-1}"
STATES="${QUEUE_COMPILE_STATES:-published_ready,candidate}"
START_INDEX="${QUEUE_COMPILE_START_INDEX:-1}"
MAX_TARGETS="${QUEUE_COMPILE_MAX_TARGETS:-0}"
INCLUDE_PATHS=()
RUN_DIR="${QUEUE_COMPILE_RUN_DIR:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --write-report) WRITE_REPORT="$2"; shift 2 ;;
    --latex-command) LATEX_COMMAND="$2"; shift 2 ;;
    --timeout-seconds) TIMEOUT_SECONDS="$2"; shift 2 ;;
    --passes) PASSES="$2"; shift 2 ;;
    --jobs) JOBS="$2"; shift 2 ;;
    --states) STATES="$2"; shift 2 ;;
    --start-index) START_INDEX="$2"; shift 2 ;;
    --max-targets) MAX_TARGETS="$2"; shift 2 ;;
    --include-path) INCLUDE_PATHS+=("$2"); shift 2 ;;
    --run-dir) RUN_DIR="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [[ "$JOBS" != "1" ]]; then
  echo "queue compile smoke currently runs sequentially in this cloudtainer-safe live runner; ignoring --jobs $JOBS" >&2
fi
ROOT_ABS="$(cd "$ROOT" && pwd)"
CMD=(python3 -B "$ROOT_ABS/publishing/check_queue_compile_smoke.py" --root "$ROOT_ABS" --run-live --latex-command "$LATEX_COMMAND" --timeout-seconds "$TIMEOUT_SECONDS" --passes "$PASSES" --states "$STATES" --start-index "$START_INDEX" --max-targets "$MAX_TARGETS")
for path in "${INCLUDE_PATHS[@]}"; do
  CMD+=(--include-path "$path")
done
if [[ -n "$RUN_DIR" ]]; then
  CMD+=(--run-dir "$RUN_DIR")
fi
if [[ -n "$WRITE_REPORT" ]]; then
  CMD+=(--write-report "$WRITE_REPORT")
fi
exec "${CMD[@]}"
