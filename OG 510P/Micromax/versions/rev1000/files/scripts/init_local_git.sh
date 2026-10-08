#!/usr/bin/env bash
set -euo pipefail

if ! command -v git >/dev/null 2>&1; then
  echo "git not found"
  exit 1
fi

if [ -d .git ]; then
  echo "Already a git repo"
  exit 0
fi

git init

git add .
git commit -m "micromax: bootstrap" || true

echo "Initialized local git repo (no remote)."
