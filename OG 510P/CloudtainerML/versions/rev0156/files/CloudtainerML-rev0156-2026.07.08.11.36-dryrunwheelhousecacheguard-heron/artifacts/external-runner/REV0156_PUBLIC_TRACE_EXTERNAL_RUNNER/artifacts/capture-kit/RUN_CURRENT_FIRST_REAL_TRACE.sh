#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/REV0156_FIRST_REAL_TRACE_ONE_COMMAND.sh" "$@"
