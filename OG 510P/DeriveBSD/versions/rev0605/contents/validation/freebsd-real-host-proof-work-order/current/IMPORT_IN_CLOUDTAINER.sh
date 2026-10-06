#!/bin/sh
set -eu

# Run this in the cloudtainer with the same DeriveBSD tree after the archive
# from RUN_ON_FREEBSD.sh has been copied back.
# Usage: sh IMPORT_IN_CLOUDTAINER.sh [/path/to/DeriveBSD] [archive.zip]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${1:-$(pwd)}
ARCHIVE=${2:-derivebsd-freebsd-host-proof-handoff.zip}
PYTHON=${PYTHON:-python3}

cd "$REPO_ROOT"

"$SCRIPT_DIR/VERIFY_WORK_ORDER.sh" "$REPO_ROOT" "$SCRIPT_DIR"

"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/preflight_sealed_removable_media_local_fallback_host_proof_import.py" \
  "$ARCHIVE" \
  --import-root "validation/freebsd-host-proof-imports" \
  --require-primary-target \
  --reuse-existing-import
"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py" \
  "$ARCHIVE" \
  --import-root "validation/freebsd-host-proof-imports" \
  --require-primary-target \
  --reuse-existing-import
"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py" \
  "validation/freebsd-host-proof-imports" \
  --require-primary-target
"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/report_removable_media_local_fallback_host_proof_imports.py" \
  --fail-if-incomplete
"$PYTHON" -B -S "$REPO_ROOT/tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py"
"$PYTHON" -B -S "$REPO_ROOT/tools/check_freebsd_real_host_proof_theatre_gate.py"

printf '%s
' "primary-production real FreeBSD host proof imported and gated"
