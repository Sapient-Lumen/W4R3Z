#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/REV0156_RUN_TINYLLAMA_PUBLIC_TRACE.sh" "$@"
