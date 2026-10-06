#!/bin/sh
# Collect a strict real FreeBSD host-smoke receipt and finalize an importable proof bundle.
# This wrapper intentionally passes no non-proof validator/finalizer flags.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd -P)
PYTHON=${PYTHON:-python3}
OUT=${1:-"$ROOT/validation/removable-media-local-freebsd-host-smoke.real-host.json"}
BUNDLE=${2:-"$ROOT/validation/removable-media-local-freebsd-host-proof.bundle.json"}
HANDOFF_DIR=${3:-${DERIVEBSD_HOST_PROOF_HANDOFF_DIR:-}}
GENERATED_AT=${GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}
HANDOFF_REPLACE=${DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE:-0}

collector_refuse() {
  printf '%s\n' "host-proof collector refused: $*" >&2
  exit 2
}

# Emits the shared: must not contain existing symlink components before host proof work
guard_operator_path_components() {
  [ -n "$1" ] || return 0
  path_guard_error=$("$PYTHON" -B -S -c '
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "tools" / "freebsd"))
import host_proof_contract as contract
try:
    contract.require_no_existing_symlink_component(Path(sys.argv[2]), sys.argv[3])
except Exception as exc:
    print(exc, file=sys.stderr)
    raise SystemExit(2)
' "$ROOT" "$1" "$2" 2>&1) || collector_refuse "$path_guard_error"
}

guard_handoff_collision() {
  [ -n "$HANDOFF_DIR" ] || return 0
  if [ -L "$HANDOFF_DIR" ]; then
    collector_refuse "handoff directory must not be a symlink before host proof collection: $HANDOFF_DIR"
  fi
  guard_operator_path_components "$HANDOFF_DIR" "handoff directory"
  if [ -e "$HANDOFF_DIR" ] && [ ! -d "$HANDOFF_DIR" ]; then
    collector_refuse "handoff path exists but is not a directory: $HANDOFF_DIR"
  fi
  [ "$HANDOFF_REPLACE" = "1" ] && return 0
  for name in receipt.json bundle.json SHA256SUMS README.import.txt; do
    if [ -e "$HANDOFF_DIR/$name" ]; then
      collector_refuse "refusing to overwrite existing handoff file: $HANDOFF_DIR/$name (set DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=1 only for deliberate replacement)"
    fi
  done
}

guard_handoff_collision

"$ROOT/tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh"

if [ -n "$HANDOFF_DIR" ]; then
  mkdir -p "$HANDOFF_DIR"
  guard_handoff_collision
  OUT="$HANDOFF_DIR/receipt.json"
  BUNDLE="$HANDOFF_DIR/bundle.json"
fi

"$PYTHON" -B -S "$ROOT/tools/freebsd/run_removable_media_local_fallback_host_smoke.py" \
  --run-host-smoke \
  --output "$OUT" \
  --generated-at "$GENERATED_AT"

"$PYTHON" -B -S "$ROOT/tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py" "$OUT"
"$PYTHON" -B -S "$ROOT/tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py" \
  "$OUT" \
  --output "$BUNDLE" \
  --generated-at "$GENERATED_AT"
"$PYTHON" -B -S "$ROOT/tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py" \
  "$BUNDLE" \
  --receipt "$OUT"

if command -v sha256 >/dev/null 2>&1; then
  receipt_digest=$(sha256 -q "$OUT")
  bundle_digest=$(sha256 -q "$BUNDLE")
elif command -v sha256sum >/dev/null 2>&1; then
  receipt_digest=$(sha256sum "$OUT" | awk '{print $1}')
  bundle_digest=$(sha256sum "$BUNDLE" | awk '{print $1}')
else
  receipt_digest="unavailable"
  bundle_digest="unavailable"
fi

if [ -n "$HANDOFF_DIR" ]; then
  {
    printf '%s  receipt.json\n' "$receipt_digest"
    printf '%s  bundle.json\n' "$bundle_digest"
  } > "$HANDOFF_DIR/SHA256SUMS"
  "$PYTHON" -B -S "$ROOT/tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py" "$HANDOFF_DIR"
  printf 'handoff=%s\n' "$HANDOFF_DIR"
fi

printf 'receipt=%s\n' "$OUT"
printf 'receipt_sha256:%s\n' "$receipt_digest"
printf 'bundle=%s\n' "$BUNDLE"
printf 'bundle_sha256:%s\n' "$bundle_digest"
