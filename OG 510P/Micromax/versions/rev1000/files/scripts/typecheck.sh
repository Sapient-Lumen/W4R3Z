#!/usr/bin/env bash
set -euo pipefail

if command -v mypy >/dev/null 2>&1; then
  mypy src/micromax src/micromax_editor tests tools
else
  echo "typecheck: mypy not installed (offline environment). Skipping."
fi
