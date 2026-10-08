#!/usr/bin/env bash
set -euo pipefail

if ! command -v git >/dev/null 2>&1; then
  echo "git not found in PATH" >&2
  exit 1
fi

if [ -d .git ]; then
  echo ".git already exists" >&2
  exit 0
fi

git init

git add -A

git commit -m "Initial micromax snapshot" 2>/dev/null || true

echo "Initialized local git repository."
echo "Tip: run 'make test' before commits."
