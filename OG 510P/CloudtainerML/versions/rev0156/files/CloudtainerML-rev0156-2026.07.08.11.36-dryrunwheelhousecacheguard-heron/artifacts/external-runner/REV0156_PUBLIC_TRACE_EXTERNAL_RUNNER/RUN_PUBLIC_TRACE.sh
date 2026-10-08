#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
export CAPTURE_LOCAL_ONLY="${CAPTURE_LOCAL_ONLY:-1}"
export ALLOW_DOWNLOAD=0
exec bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh "$@"
