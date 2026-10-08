#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip

# Offline-friendly: try to install dev deps, but don't fail the whole bootstrap if it can't reach PyPI.
set +e
python -m pip install -e '.[dev]'
status=$?
set -e

if [ $status -ne 0 ]; then
  echo "bootstrap: couldn't install dev deps (likely offline)."
  echo "bootstrap: tests still work; lint/format/typecheck will use lightweight fallbacks where possible."
else
  echo "bootstrap: dev deps installed."
fi

echo "Bootstrap complete."
