#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0661 receipt gated materialization package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=134 failed=0"
ACTIVE_BINARY = "bin/rev0661/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0660/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0661-receipt-gated-materialization-audit.json"
MANIFEST = ROOT / "schema/rev0661/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0051-rev0661-receipt-gated-materialization.md",
    "audit/rev0661-receipt-gated-materialization-audit.json",
    "audit/rev0661-receipt-gated-materialization-source.patch",
    "audit/logs/rev0661-release-o0-configure.log",
    "audit/logs/rev0661-release-o0-build.log",
    "audit/logs/rev0661-release-o0-ctest.log",
    "audit/logs/rev0661-receipt-gated-materialization-selftest.log",
    "audit/logs/rev0661-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0661-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0661-binary-sha256.txt",
    "audit/logs/rev0661-binary-ldd.txt",
    "audit/logs/rev0661-receipt-gated-materialization-package-validator.log",
    "tools/validate_rev0661_receipt_gated_materialization.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0661",
        "receipt-gated materialization",
        "require_chunk_receipts",
        "verify_staged_file_complete_with_receipts_or_throw",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0661",
        "SyncStagedFileMaterializationOptions",
        "SyncConflictPreservationOptions",
        "optional receipt-gated commit checks",
        "optional receipt-gated remote file promotion",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "bool require_chunk_receipts = false;",
        "bool chunk_receipts_checked = false;",
        "struct SyncStagedFileMaterializationOptions",
        "struct SyncConflictPreservationOptions",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "options.require_chunk_receipts",
        "verify_staged_file_complete_with_receipts_or_throw",
        "receipt-gated staged file materialization rejects complete staged bytes without chunk receipts",
        "completed chunk receipt staging file can be materialized only after receipt-gated verification",
        "receipt-gated conflict preservation requires chunk receipts before promoting remote conflict bytes",
    ],
    "docs/0051-rev0661-receipt-gated-materialization.md": [
        "C++ receipt-gated materialization",
        "require_chunk_receipts",
        "complete but unreceipted staged file",
        "does not persist transfer state",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "receipt-gated staged-file materialization",
        "receipt-gated materialization",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0661",
        "receipt-gated materialization",
        "receipt sidecar garbage collection after commit",
    ],
    "bin/HISTORY.md": [
        "rev0661",
        "receipt-gated materialization",
        "rev0660: historical source/audit only",
    ],
    "audit/rev0661-receipt-gated-materialization-audit.json": [
        "receipt-gated-materialization",
        "fixed_by_optional_receipt_gated_materialization",
        "fixed_by_require_chunk_receipts_option_on_apply_sync_conflict_preservation",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_exists() -> None:
    missing = [path for path in REQUIRED_CURRENT_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0661 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0661 package must not carry the rev0660 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0661-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0661-receipt-gated-materialization-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0661-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0661-receipt-gated-materialization-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0661" or audit.get("parent_revision") != "rev0660":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0661 must claim C++ behavior changed")
    required_api = {
        "SyncStagedFileMaterializationOptions adds require_chunk_receipts for receipt-gated staged-file commits",
        "SyncStagedFileMaterializationResult adds chunk_receipts_checked evidence",
        "SyncConflictPreservationOptions adds require_chunk_receipts for receipt-gated remote conflict file promotion",
        "SyncConflictPreservationResult adds chunk_receipts_checked evidence",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("chunk_receipts_were_not_required_at_final_materialization") != "fixed_by_optional_receipt_gated_materialization":
        raise AssertionError("audit must record final materialization receipt gate")
    if findings.get("complete_staged_bytes_could_bypass_chunk_receipt_evidence") != "fixed_by_require_chunk_receipts_option_on_materialize_staged_sync_file":
        raise AssertionError("audit must record staged byte receipt bypass fix")
    if findings.get("remote_conflict_file_promotion_could_bypass_receipt_evidence") != "fixed_by_require_chunk_receipts_option_on_apply_sync_conflict_preservation":
        raise AssertionError("audit must record conflict promotion receipt gate")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0661-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0661" or manifest.get("parent_revision") != "rev0660":
        raise AssertionError("rev0661 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-receipt-gated-materialization":
        raise AssertionError("rev0661 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0661 product mission tag mismatch")
    if manifest.get("codename") != "receipt-gated-materialization":
        raise AssertionError("rev0661 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0661")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0661 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0660 active binary")
    if "schema/rev0661/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    for row in rows:
        rel = row["path"]
        p = ROOT / rel
        if not p.exists():
            raise AssertionError(f"manifest file missing on disk: {rel}")
        data = p.read_bytes()
        if len(data) != row["size_bytes"]:
            raise AssertionError(f"manifest size mismatch: {rel}")
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"manifest sha mismatch: {rel}")


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_binary_sha()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
