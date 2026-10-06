#!/bin/sh
set -eu

# Run this from a real FreeBSD host with a checked-out DeriveBSD tree.
# Usage: sh RUN_ON_FREEBSD.sh [/path/to/DeriveBSD] [/tmp/handoff-dir] [archive.zip]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${1:-$(pwd)}
HANDOFF_DIR=${2:-/tmp/derivebsd-host-proof-handoff}
ARCHIVE=${3:-derivebsd-freebsd-host-proof-handoff.zip}
PYTHON=${PYTHON:-python3}

run_root_collector() {
  uid=$(/usr/bin/id -u 2>/dev/null || id -u 2>/dev/null || printf unknown)
  if [ "$uid" = "0" ]; then
    env PYTHON="$PYTHON" DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=${DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE:-0} "$REPO_ROOT/tools/freebsd/collect_removable_media_local_fallback_host_proof.sh" "$HANDOFF_DIR/receipt.json" "$HANDOFF_DIR/bundle.json" "$HANDOFF_DIR"
  else
    if ! command -v sudo >/dev/null 2>&1; then
      printf '%s\n' "host-proof collection FAILED: run as root or install sudo; observed uid $uid" >&2
      exit 1
    fi
    sudo env PYTHON="$PYTHON" DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=${DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE:-0} "$REPO_ROOT/tools/freebsd/collect_removable_media_local_fallback_host_proof.sh" "$HANDOFF_DIR/receipt.json" "$HANDOFF_DIR/bundle.json" "$HANDOFF_DIR"
  fi
}

cd "$REPO_ROOT"

# Verify the copied work-order kit and run the root FreeBSD preflight before
# collection.  This avoids a split where collection runs through sudo but the
# root-required preflight runs as the invoking user.
"$SCRIPT_DIR/PREFLIGHT_ON_FREEBSD.sh" "$REPO_ROOT"

# Collect the scarce evidence.  This path intentionally uses no checker-only or
# failed/refusal proof flags.
run_root_collector

"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py" "$HANDOFF_DIR"
"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py" "$HANDOFF_DIR" --output "$ARCHIVE"

printf '%s\n' "real FreeBSD host-proof handoff sealed: $ARCHIVE"
printf '%s\n' "bring this archive back to the cloudtainer and run IMPORT_IN_CLOUDTAINER.sh"
