#!/bin/sh
# Fail-fast operator preflight for the real FreeBSD removable-media host proof.
# This script is intentionally read-only: it checks host identity, tool paths,
# Python importability, fixture presence, and root privilege before the collector
# creates md(4) devices or mounts a disposable image.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd -P)
PYTHON=${PYTHON:-python3}

fail() {
  printf '%s\n' "host-proof preflight FAILED: $*" >&2
  exit 1
}

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_executable_path() {
  [ -x "$1" ] || fail "missing required executable path: $1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command on PATH: $1"
}

require_command "$PYTHON"

CONTRACT_VALUES=$(
  "$PYTHON" -B -S -c 'import sys, pathlib; root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "tools" / "freebsd")); import host_proof_contract as c; print(c.MIN_FREEBSD_OSRELDATE, c.SUPPORTED_FREEBSD_RELEASE_FLOOR, c.PRIMARY_FREEBSD_RELEASE, c.PRIMARY_FREEBSD_OSRELDATE_MINIMUM, c.HOST_TARGET_MATRIX_ID)' "$ROOT"
) || fail "could not read host proof contract with $PYTHON"
set -- $CONTRACT_VALUES
MIN_OSRELDATE=$1
RELEASE_FLOOR=$2
PRIMARY_RELEASE=$3
PRIMARY_OSRELDATE=$4
TARGET_MATRIX_ID=$5

system=$(/bin/uname -s 2>/dev/null || uname -s 2>/dev/null || printf unknown)
[ "$system" = "FreeBSD" ] || fail "requires FreeBSD host, observed $system"

uid=$(/usr/bin/id -u 2>/dev/null || id -u 2>/dev/null || printf unknown)
[ "$uid" = "0" ] || fail "requires root so mdconfig/mount authority is explicit, observed uid $uid"

require_executable_path /bin/uname
require_executable_path /usr/bin/id
require_executable_path /sbin/sysctl
require_executable_path /usr/bin/cc
require_executable_path /usr/sbin/makefs
require_executable_path /sbin/mdconfig
require_executable_path /usr/sbin/fstyp
require_executable_path /sbin/mount
require_executable_path /sbin/umount
if ! command -v sha256 >/dev/null 2>&1 && ! command -v sha256sum >/dev/null 2>&1; then
  fail "requires sha256 or sha256sum for handoff SHA256SUMS"
fi

osreldate=$(/sbin/sysctl -n kern.osreldate 2>/dev/null || printf unknown)
case "$osreldate" in
  *[!0-9]*|'') fail "kern.osreldate must be numeric, observed $osreldate" ;;
esac
[ "$osreldate" -ge "$MIN_OSRELDATE" ] || fail "kern.osreldate $osreldate is below supported floor $MIN_OSRELDATE ($RELEASE_FLOOR)"

release=$(/bin/uname -r 2>/dev/null || uname -r 2>/dev/null || printf unknown)
target_tier=supported-legacy-floor
case "$release" in
  "$PRIMARY_RELEASE"*)
    if [ "$osreldate" -ge "$PRIMARY_OSRELDATE" ]; then
      target_tier=primary-production
    fi
    ;;
esac

cap_mode=$(/sbin/sysctl -n kern.features.security_capability_mode 2>/dev/null || printf unknown)
cap_caps=$(/sbin/sysctl -n kern.features.security_capabilities 2>/dev/null || printf unknown)
[ "$cap_mode" = "1" ] || fail "kern.features.security_capability_mode must be 1, observed $cap_mode"
[ "$cap_caps" = "1" ] || fail "kern.features.security_capabilities must be 1, observed $cap_caps"

require_file "$ROOT/tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh"
require_file "$ROOT/tools/freebsd/write_collect_import_run_receipt.py"
require_file "$ROOT/tools/freebsd/validate_collect_import_run_receipt.py"
require_file "$ROOT/tools/freebsd/run_removable_media_local_fallback_host_smoke.py"
require_file "$ROOT/tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py"
require_file "$ROOT/tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py"
require_file "$ROOT/tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py"
require_file "$ROOT/tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py"
require_file "$ROOT/tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py"
require_file "$ROOT/tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py"
require_file "$ROOT/tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py"
require_file "$ROOT/tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py"
require_file "$ROOT/tools/freebsd/rm_post_detach_capsicum_worker.c"
require_file "$ROOT/fixtures/removable-media/local-fallback/exfat-card/invoice.pdf"

"$PYTHON" -B -S "$ROOT/tools/freebsd/run_removable_media_local_fallback_host_smoke.py" --help >/dev/null || fail "host-smoke runner is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py" --help >/dev/null || fail "host-smoke receipt validator is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py" --help >/dev/null || fail "proof-bundle finalizer is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py" --help >/dev/null || fail "handoff verifier is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py" --help >/dev/null || fail "handoff sealer is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py" --help >/dev/null || fail "handoff unsealer is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py" --help >/dev/null || fail "handoff importer is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py" --help >/dev/null || fail "import-root auditor is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/write_collect_import_run_receipt.py" --help >/dev/null || fail "run receipt writer is not importable with $PYTHON -B -S"
"$PYTHON" -B -S "$ROOT/tools/freebsd/validate_collect_import_run_receipt.py" --help >/dev/null || fail "run receipt validator is not importable with $PYTHON -B -S"
"$ROOT/tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh" --help >/dev/null || fail "strict collect/import wrapper help failed"

printf '%s\n' "host-proof preflight OK: FreeBSD $release osreldate=$osreldate target_tier=$target_tier matrix=$TARGET_MATRIX_ID floor=$RELEASE_FLOOR primary=$PRIMARY_RELEASE, root, Capsicum sysctls enabled, proof tools importable"
