#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 REPO_DIR OUTPUT_ZIP" >&2
  exit 1
fi

REPO_DIR="$1"
OUTPUT_ZIP="$2"
BASE_DIR="$(dirname "$REPO_DIR")"
NAME="$(basename "$REPO_DIR")"

rm -f "$OUTPUT_ZIP"
(
  cd "$BASE_DIR"
  zip -qr "$OUTPUT_ZIP" "$NAME" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store' '*/.pytest_cache/*'
)

echo "$OUTPUT_ZIP"
