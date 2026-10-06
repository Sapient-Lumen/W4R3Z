"""Shared FreeBSD host-proof contract constants.

Keep the proof-tool set, cube cut, runner contract, and handoff filenames in one
place so the finalizer, validators, import verifier, and release-critical checks
cannot silently drift apart.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
TOOLS = THIS_DIR.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cube_digest_lib import canonical_digest  # noqa: E402

CURRENT_CUBE_CUT_VERSION = "2026-06-18r630"
RUNNER_CONTRACT_VERSION = "2026-06-05r554"
MIN_FREEBSD_OSRELDATE = 1404000
SUPPORTED_FREEBSD_RELEASE_FLOOR = "14.4-RELEASE"
SUPPORTED_FREEBSD_RELEASE_FLOOR_EOL = "2026-12-31"
PREVIOUS_FREEBSD_RELEASE_FLOOR = "14.3-RELEASE"
PREVIOUS_FREEBSD_RELEASE_FLOOR_EOL = "2026-06-30"
HOST_RELEASE_FLOOR_POLICY = "require-kern-osreldate-at-or-above-supported-floor-before-media-authority"

PRIMARY_FREEBSD_RELEASE = "15.1-RELEASE"
PRIMARY_FREEBSD_RELEASE_EOL = "2027-03-31"
PRIMARY_FREEBSD_OSRELDATE_MINIMUM = 1501500
PRIMARY_FREEBSD_RELEASE_CHANNEL = "production"
HOST_TARGET_MATRIX_ID = "freebsd-host-proof-targets-20260617-r605"
HOST_TARGET_TIER_POLICY = "accept-supported-floor-but-label-primary-production-versus-legacy-floor"
HOST_TARGET_PRIMARY_TIER = "primary-production"
HOST_TARGET_LEGACY_TIER = "supported-legacy-floor"
HOST_TARGET_UNSUPPORTED_TIER = "unsupported"


def classify_host_target(uname_release: str | None, osreldate_value: str | int | None) -> str:
    """Classify a probed FreeBSD host against the current proof target matrix.

    The supported floor keeps scarce proof collection possible on older supported
    hosts, but the receipt must not hide whether it came from the current
    production target or merely from the legacy floor.
    """
    try:
        osreldate = int(str(osreldate_value))
    except (TypeError, ValueError):
        return HOST_TARGET_UNSUPPORTED_TIER
    release = str(uname_release or "")
    if release.startswith(PRIMARY_FREEBSD_RELEASE) and osreldate >= PRIMARY_FREEBSD_OSRELDATE_MINIMUM:
        return HOST_TARGET_PRIMARY_TIER
    if osreldate >= MIN_FREEBSD_OSRELDATE:
        return HOST_TARGET_LEGACY_TIER
    return HOST_TARGET_UNSUPPORTED_TIER

def cube_release_token(version: str = CURRENT_CUBE_CUT_VERSION) -> str:
    """Return the canonical YYYYMMDD-rNNN token used by generated IDs."""
    date_part, separator, revision = version.partition("r")
    if not separator or len(date_part) != 10 or not revision.isdigit():
        raise ValueError(f"invalid cube cut version: {version!r}")
    return f"{date_part.replace('-', '')}-r{revision}"


BUNDLE_KIND = "removable.media.local.freebsd.host.proof.bundle"
BUNDLE_SCHEMA_VERSION = "0.1"
BUNDLE_ID = f"rm-local-freebsd-host-proof-bundle-{cube_release_token()}"

RECEIPT_NAME = "receipt.json"
BUNDLE_NAME = "bundle.json"
SUMS_NAME = "SHA256SUMS"
README_NAME = "README.import.txt"
IMPORT_RECEIPT_NAME = "import.receipt.json"
DEFAULT_IMPORT_ROOT_REL = "validation/freebsd-host-proof-imports"
IMPORT_RECEIPT_KIND = "removable.media.local.freebsd.host.proof.handoff.import.receipt"
IMPORT_RECEIPT_SCHEMA_VERSION = "0.1"
DIRECTORY_IMPORT_SOURCE_KIND = "unsealed-handoff-directory"
SEALED_IMPORT_SOURCE_KIND = "deterministic-sealed-handoff-archive"
SEALED_IMPORT_POLICY = "sealed-archive-nofollow-snapshot-validate-unseal-import-audit-cleanup"
SEALED_IMPORT_PRIMARY_TARGET_POLICY = "sealed-importer-rechecks-primary-target-after-snapshot-and-before-publish"
SEALED_IMPORT_FAILURE_CLEANUP_POLICY = "failed-post-import-audit-removes-newly-published-import-unless-operator-keeps-forensics"
SEALED_IMPORT_EXISTING_REUSE_POLICY = "existing-digest-import-reused-only-after-audit-clean-matching-sealed-archive-digest"
SEALED_IMPORT_LOCK_POLICY = "exclusive-sibling-lock-serializes-sealed-import-publish-reuse-and-replace"
SEALED_IMPORT_PREFLIGHT_POLICY = "sealed-archive-preflight-snapshots-unseals-reverifies-and-predicts-import-identity-without-publish"
IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY = "import-receipt-binds-source-transport-kind-path-and-digest-where-applicable"
DIRECTORY_IMPORT_COPY_POLICY = "directory-import-copies-allowed-regular-files-via-dirfd-nofollow-into-staging-before-reverify"
IMPORT_RECEIPT_SNAPSHOT_KIND = "freebsd-host-proof-import-copied-handoff-snapshot"
IMPORT_RECEIPT_SNAPSHOT_POLICY = "import-receipt-binds-copied-handoff-file-manifest-count-total-bytes-and-canonical-digest"
IMPORT_DURABLE_WRITE_POLICY = "fsync-copied-handoff-files-import-receipt-and-parent-directories-before-and-after-atomic-publish"
IMPORT_STAGED_IDENTITY_POLICY = "import-directory-name-receipt-summaries-and-bundle-summaries-derive-from-reverified-copied-handoff-snapshot"
IMPORT_DIRECTORY_DIGEST_HEX_LENGTH = 64
IMPORT_DIRECTORY_DIGEST_POLICY = "import-directory-name-binds-proof-status-and-full-copied-handoff-snapshot-canonical-digest"
HANDOFF_REQUIRED_NAMES = frozenset({RECEIPT_NAME, BUNDLE_NAME, SUMS_NAME})
HANDOFF_OPTIONAL_NAMES = frozenset({README_NAME})
HANDOFF_ALLOWED_NAMES = HANDOFF_REQUIRED_NAMES | HANDOFF_OPTIONAL_NAMES
HANDOFF_CHECKSUM_REQUIRED_NAMES = frozenset({RECEIPT_NAME, BUNDLE_NAME})
HANDOFF_CHECKSUM_OPTIONAL_NAMES = frozenset({README_NAME})
HANDOFF_CHECKSUM_ALLOWED_NAMES = HANDOFF_CHECKSUM_REQUIRED_NAMES | HANDOFF_CHECKSUM_OPTIONAL_NAMES
HANDOFF_CHECKSUM_POLICY = "sha256sums-covers-required-members-and-every-present-optional-member"

HANDOFF_REPLACE_ENV = "DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE"
HANDOFF_OVERWRITE_GUARD_POLICY = "refuse-to-overwrite-existing-handoff-members-before-freebsd-preflight-unless-explicit-replace"

HANDOFF_ARCHIVE_FORMAT = "derivebsd-freebsd-host-proof-handoff-zip-v1"
HANDOFF_ARCHIVE_FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)
HANDOFF_ARCHIVE_FIXED_FILE_MODE = 0o100644
MAX_HANDOFF_MEMBER_BYTES = 4 * 1024 * 1024
MAX_HANDOFF_ARCHIVE_BYTES = 16 * 1024 * 1024
HANDOFF_ARCHIVE_SIZE_POLICY = "reject-transport-archives-or-members-above-finite-host-proof-handoff-limits"
HANDOFF_SEAL_SNAPSHOT_POLICY = "seal-from-nofollow-copied-handoff-snapshot-verified-before-archive-write"
HANDOFF_ARCHIVE_SNAPSHOT_KIND = "freebsd-host-proof-sealed-archive-snapshot"
HANDOFF_ARCHIVE_SNAPSHOT_POLICY = "copy-sealed-archive-via-nofollow-bounded-snapshot-before-zip-validation"
HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY = "reject-zip-comments-extra-fields-non-unix-origin-noncanonical-entry-order-and-nonregular-file-mode-before-unseal-or-import"
OPERATOR_PATH_SYMLINK_ANCESTOR_POLICY = "reject-existing-symlink-components-before-host-proof-collection-seal-unseal-or-import"


def first_existing_symlink_component(path: Path) -> Path | None:
    """Return the first existing symlink component in an operator path.

    These host-proof tools may create the final directory or file, so the check
    walks only the existing prefix of the user supplied path.  It intentionally
    does not resolve the path first: resolving would hide the exact symlink that
    could redirect scarce real-host evidence before later proof checks run.
    """
    raw = path.expanduser()
    candidate = raw if raw.is_absolute() else Path.cwd() / raw
    current = Path(candidate.anchor or ".")
    parts = candidate.parts[1:] if candidate.anchor else candidate.parts
    for part in parts:
        current = current / part
        try:
            if current.is_symlink():
                return current
            if not current.exists():
                return None
        except OSError as exc:
            raise ValueError(f"could not inspect operator path component {current}: {exc}") from exc
    return None


def require_no_existing_symlink_component(path: Path, purpose: str) -> None:
    """Reject operator paths whose existing prefix includes any symlink."""
    symlink_component = first_existing_symlink_component(path)
    if symlink_component is not None:
        raise ValueError(
            f"{purpose} must not contain existing symlink components before host proof work: {symlink_component}"
        )



def sha256_file(path: Path) -> str:
    """Return the DeriveBSD sha256:<hex> digest for a finite local file."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def copied_handoff_snapshot(imported_handoff: Path) -> dict[str, Any]:
    """Return the canonical manifest for a copied FreeBSD proof handoff.

    Import identity, import receipts, and import audits all depend on this same
    byte manifest.  Keeping it here prevents the importer and auditor from
    drifting on which optional handoff files are identity-bearing.
    """
    rows: list[dict[str, Any]] = []
    total_size = 0
    for name in sorted(HANDOFF_ALLOWED_NAMES):
        path = imported_handoff / name
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"copied handoff member must be a regular file: {path}")
        size = path.stat().st_size
        total_size += size
        rows.append({"path": f"handoff/{name}", "sha256": sha256_file(path), "size_bytes": size})
    manifest_core = {
        "kind": IMPORT_RECEIPT_SNAPSHOT_KIND,
        "snapshot_policy": IMPORT_RECEIPT_SNAPSHOT_POLICY,
        "file_count": len(rows),
        "total_size_bytes": total_size,
        "files": rows,
    }
    return {**manifest_core, "canonical_sha256": canonical_digest(manifest_core)}


def handoff_file_rows(imported_handoff: Path) -> list[dict[str, str]]:
    """Return the import-receipt file rows for the shared copied handoff snapshot."""
    return [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in copied_handoff_snapshot(imported_handoff)["files"]
    ]


def import_status_prefix(proof_status: str) -> str:
    """Return the only import directory prefix allowed for a proof status."""
    if proof_status == "real-host-proof":
        return "real-host-proof"
    if proof_status == "checker-simulation-non-proof":
        return "checker-simulation-non-proof"
    return "unknown-proof-status"


def _canonical_sha256_hex(canonical_sha256: str) -> str:
    """Return a full 64-hex SHA-256 digest body from a canonical digest string."""
    if not canonical_sha256.startswith("sha256:"):
        raise ValueError("canonical identity digest must be sha256:<64-hex>")
    digest_hex = canonical_sha256.removeprefix("sha256:")
    if len(digest_hex) != IMPORT_DIRECTORY_DIGEST_HEX_LENGTH or any(ch not in "0123456789abcdef" for ch in digest_hex):
        raise ValueError("canonical identity digest must be lowercase 64-hex SHA-256")
    return digest_hex


def import_directory_name(proof_status: str, copied_handoff_snapshot_canonical_sha256: str) -> str:
    """Return the finite import directory name for a verified handoff.

    Import paths are evidence identity, not UX labels.  Use the full canonical
    digest of the reverified copied handoff snapshot so a future real-host
    import cannot collide when receipt.json is unchanged but bundle.json,
    README.import.txt, or checksum bytes differ under the same proof-status
    namespace.
    """
    return f"{import_status_prefix(proof_status)}-{_canonical_sha256_hex(copied_handoff_snapshot_canonical_sha256)}"

HOST_SMOKE_VALIDATOR_REL = "tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py"
HOST_SMOKE_RUNNER_REL = "tools/freebsd/run_removable_media_local_fallback_host_smoke.py"
HOST_SMOKE_COLLECTOR_REL = "tools/freebsd/collect_removable_media_local_fallback_host_proof.sh"
HOST_PROOF_FINALIZER_REL = "tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py"
HOST_PROOF_BUNDLE_VALIDATOR_REL = "tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py"
HOST_PROOF_HANDOFF_VERIFIER_REL = "tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py"
HOST_PROOF_HANDOFF_SEALER_REL = "tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py"
HOST_PROOF_HANDOFF_UNSEALER_REL = "tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py"
HOST_PROOF_HANDOFF_IMPORTER_REL = "tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py"
HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL = "tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py"
HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL = "tools/freebsd/preflight_sealed_removable_media_local_fallback_host_proof_import.py"
HOST_PROOF_IMPORT_AUDITOR_REL = "tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py"
HOST_PROOF_IMPORT_STATUS_REPORTER_REL = "tools/freebsd/report_removable_media_local_fallback_host_proof_imports.py"
HOST_PROOF_CONTRACT_REL = "tools/freebsd/host_proof_contract.py"
HOST_PROOF_PREFLIGHT_REL = "tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh"
HOST_PROOF_COLLECT_IMPORT_REL = "tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh"
HOST_PROOF_RUN_RECEIPT_WRITER_REL = "tools/freebsd/write_collect_import_run_receipt.py"
HOST_PROOF_RUN_RECEIPT_VALIDATOR_REL = "tools/freebsd/validate_collect_import_run_receipt.py"
HOST_PROOF_WORK_ORDER_STAGER_REL = "tools/freebsd/stage_real_host_proof_work_order.py"
HOST_PROOF_WORK_ORDER_VERIFIER_REL = "tools/freebsd/verify_real_host_proof_work_order.py"
HOST_PROOF_CHECKED_IMPORT_GATE_REL = "tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py"
HOST_PROOF_THEATRE_GATE_REL = "tools/check_freebsd_real_host_proof_theatre_gate.py"
WORKER_SOURCE_REL = "tools/freebsd/rm_post_detach_capsicum_worker.c"

REQUIRED_PROOF_TOOL_PATHS = (
    HOST_PROOF_CONTRACT_REL,
    HOST_PROOF_PREFLIGHT_REL,
    HOST_PROOF_COLLECT_IMPORT_REL,
    HOST_PROOF_RUN_RECEIPT_WRITER_REL,
    HOST_PROOF_RUN_RECEIPT_VALIDATOR_REL,
    HOST_SMOKE_COLLECTOR_REL,
    HOST_SMOKE_RUNNER_REL,
    HOST_SMOKE_VALIDATOR_REL,
    HOST_PROOF_FINALIZER_REL,
    HOST_PROOF_BUNDLE_VALIDATOR_REL,
    HOST_PROOF_HANDOFF_VERIFIER_REL,
    HOST_PROOF_HANDOFF_SEALER_REL,
    HOST_PROOF_HANDOFF_UNSEALER_REL,
    HOST_PROOF_HANDOFF_IMPORTER_REL,
    HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL,
    HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL,
    HOST_PROOF_IMPORT_AUDITOR_REL,
    WORKER_SOURCE_REL,
)

REQUIRED_PROOF_TOOL_PATH_SET = frozenset(REQUIRED_PROOF_TOOL_PATHS)
