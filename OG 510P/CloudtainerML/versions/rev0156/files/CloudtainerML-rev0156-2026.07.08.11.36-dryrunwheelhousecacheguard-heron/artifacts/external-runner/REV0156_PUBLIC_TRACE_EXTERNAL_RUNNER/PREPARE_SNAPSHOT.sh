#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
# This is the only phase where network download may be enabled after license/source review.
exec bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh "$@"
