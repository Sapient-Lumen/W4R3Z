#!/usr/bin/env bash
set -euo pipefail

# Rebuild the worked-example support bundle to a declared fixed point.
# Earlier revisions encoded convergence as repeated commands, ignored one
# validation failure, and could leave TeX/Python transients in the source tree.
# This helper uses bounded refinement, heartbeat logs for cloudtainer runs, and
# temporary no-shell-escape TeX output.

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON:-python3}"
MAX_REFINE_PASSES=6
RUN_TEX=1
TEX_TIMEOUT_SECONDS=60

usage() {
  cat <<'EOF'
Usage: tools/rebuild_example.sh [--skip-tex] [--max-refine-passes N] [--tex-timeout-seconds N]

Rebuild worked-example artifacts until validation and artifact digests settle.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-tex)
      RUN_TEX=0
      shift
      ;;
    --max-refine-passes)
      MAX_REFINE_PASSES="${2:?missing value for --max-refine-passes}"
      shift 2
      ;;
    --tex-timeout-seconds)
      TEX_TIMEOUT_SECONDS="${2:?missing value for --tex-timeout-seconds}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$MAX_REFINE_PASSES" in
  ''|*[!0-9]*) echo "--max-refine-passes must be a positive integer" >&2; exit 2 ;;
esac
case "$TEX_TIMEOUT_SECONDS" in
  ''|*[!0-9]*) echo "--tex-timeout-seconds must be a positive integer" >&2; exit 2 ;;
esac
if [ "$MAX_REFINE_PASSES" -lt 1 ]; then
  echo "--max-refine-passes must be at least 1" >&2
  exit 2
fi
if [ "$TEX_TIMEOUT_SECONDS" -lt 1 ]; then
  echo "--tex-timeout-seconds must be at least 1" >&2
  exit 2
fi

export PYTHONDONTWRITEBYTECODE=1

run_with_heartbeat() {
  label="$1"
  shift
  case "$-" in
    *e*) had_errexit=1 ;;
    *) had_errexit=0 ;;
  esac
  echo "worked-example ${label} started" >&2
  set +e
  "$@" &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      echo "worked-example ${label} running" >&2
    fi
  done
  wait "$pid"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "worked-example ${label} finished" >&2
  else
    echo "worked-example ${label} failed with ${rc}" >&2
  fi
  if [ "$had_errexit" -eq 1 ]; then
    set -e
  else
    set +e
  fi
  return "$rc"
}

artifact_digest() {
  find artifacts -type f -name '*.json' -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 sha256sum \
    | sha256sum \
    | awk '{print $1}'
}

cleanup_transients() {
  rm -f paper.aux paper.log paper.out paper.pdf paper.fls paper.fdb_latexmk paper.synctex.gz
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
  find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
}

cleanup_transients
trap cleanup_transients EXIT

run_with_heartbeat materialize "$PYTHON_BIN" -B tools/materialize_example.py
run_with_heartbeat compare-report "$PYTHON_BIN" -B tools/emit_compare_report.py

fixed_point=0
for pass in $(seq 1 "$MAX_REFINE_PASSES"); do
  before="$(artifact_digest)"
  run_with_heartbeat "refine-pass-${pass}" "$PYTHON_BIN" -B tools/refine_terminal_witnesses.py
  set +e
  run_with_heartbeat "validate-pass-${pass}" "$PYTHON_BIN" -B tools/validate_example.py
  validate_rc=$?
  set -e
  after="$(artifact_digest)"

  if [ "$validate_rc" -eq 0 ] && [ "$before" = "$after" ]; then
    fixed_point=1
    echo "worked-example artifacts fixed point after pass ${pass}"
    break
  fi
  if [ "$validate_rc" -ne 0 ]; then
    echo "worked-example validate pass ${pass} failed; continuing bounded refinement" >&2
  elif [ "$before" != "$after" ]; then
    echo "worked-example refine/validate pass ${pass} changed artifact digests" >&2
  fi
done

if [ "$fixed_point" -ne 1 ]; then
  echo "worked-example artifacts did not settle within ${MAX_REFINE_PASSES} refine passes" >&2
  exit 1
fi

if [ "$RUN_TEX" -eq 1 ]; then
  tex_tmp="$(mktemp -d "${TMPDIR:-/tmp}/worked-example-tex.XXXXXX")"
  trap 'rm -rf "$tex_tmp"; cleanup_transients' EXIT
  run_with_heartbeat tex-pass-1 timeout "$TEX_TIMEOUT_SECONDS" pdflatex -halt-on-error -interaction=nonstopmode -no-shell-escape -output-directory="$tex_tmp" paper.tex >/dev/null
  run_with_heartbeat tex-pass-2 timeout "$TEX_TIMEOUT_SECONDS" pdflatex -halt-on-error -interaction=nonstopmode -no-shell-escape -output-directory="$tex_tmp" paper.tex >/dev/null
  rm -rf "$tex_tmp"
fi

cleanup_transients
