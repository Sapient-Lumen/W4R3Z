#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
exec bash artifacts/capture-kit/REV0156_BOOTSTRAP_PUBLIC_TRACE_ENV.sh "$@"
