#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/REV0156_PREPARE_TINYLLAMA_SNAPSHOT.sh" "$@"
