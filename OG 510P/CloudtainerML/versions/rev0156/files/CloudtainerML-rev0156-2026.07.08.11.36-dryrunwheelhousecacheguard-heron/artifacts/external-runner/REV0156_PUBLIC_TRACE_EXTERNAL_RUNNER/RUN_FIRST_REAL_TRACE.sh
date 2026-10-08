#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
exec bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh "$@"
