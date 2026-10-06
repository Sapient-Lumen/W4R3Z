#!/bin/sh
set -eu

# Run this from a real FreeBSD host before spending collection time.
# Usage: sh PREFLIGHT_ON_FREEBSD.sh [/path/to/DeriveBSD]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${1:-$(pwd)}
PYTHON=${PYTHON:-python3}

run_root_preflight() {
  uid=$(/usr/bin/id -u 2>/dev/null || id -u 2>/dev/null || printf unknown)
  if [ "$uid" = "0" ]; then
    env PYTHON="$PYTHON" "$REPO_ROOT/tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh"
  else
    if ! command -v sudo >/dev/null 2>&1; then
      printf '%s\n' "host-proof preflight FAILED: run as root or install sudo; observed uid $uid" >&2
      exit 1
    fi
    sudo env PYTHON="$PYTHON" "$REPO_ROOT/tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh"
  fi
}

cd "$REPO_ROOT"

"$SCRIPT_DIR/VERIFY_WORK_ORDER.sh" "$REPO_ROOT" "$SCRIPT_DIR"
run_root_preflight

printf '%s\n' "real FreeBSD host-proof preflight passed for checked-out tree"
