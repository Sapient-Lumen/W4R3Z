#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0662 staged transfer inspection package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=137 failed=0"
ACTIVE_BINARY = "bin/rev0662/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0661/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0662-staged-transfer-inspection-audit.json"
MANIFEST = ROOT / "schema/rev0662/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0052-rev0662-staged-transfer-inspection.md",
    "audit/rev0662-staged-transfer-inspection-audit.json",
    "audit/rev0662-staged-transfer-inspection-source.patch",
    "audit/logs/rev0662-release-o0-configure.log",
    "audit/logs/rev0662-release-o0-build.log",
    "audit/logs/rev0662-release-o0-ctest.log",
    "audit/logs/rev0662-staged-transfer-inspection-selftest.log",
    "audit/logs/rev0662-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0662-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0662-binary-sha256.txt",
    "audit/logs/rev0662-binary-ldd.txt",
    "audit/logs/rev0662-staged-transfer-inspection-package-validator.log",
    "tools/validate_rev0662_staged_transfer_inspection.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0662",
        "staged-transfer inspection",
        "inspect_sync_staged_transfer",
        "missing_chunks",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0662",
        "SyncStagedTransferInspectionOptions",
        "SyncStagedTransferInspectionResult",
        "inspect_sync_staged_transfer",
        "exact manifest chunks still needed from peers",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncStagedTransferInspectionOptions",
        "struct SyncStagedTransferInspectionResult",
        "std::vector<SyncChunkRange> missing_chunks;",
        "inspect_sync_staged_transfer",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "validate_staged_remote_file_evidence",
        "staged_transfer_inspection_idempotency_key",
        "SyncValidationResult inspect_sync_staged_transfer",
        "staged transfer inspection reports reusable receipts and exact missing chunks for resume",
        "staged transfer inspection rejects a receipt whose staged bytes were tampered",
    ],
    "docs/0052-rev0662-staged-transfer-inspection.md": [
        "staged transfer inspection",
        "which chunks have receipts",
        "exact `missing_chunks`",
        "does not persist transfer state",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "staged-transfer inspection",
        "inspect_sync_staged_transfer",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0662",
        "exact missing chunks",
        "inspect_sync_staged_transfer",
    ],
    "bin/HISTORY.md": [
        "rev0662",
        "staged-transfer inspection/resume seam",
        "rev0661: historical source/audit only",
    ],
    "audit/rev0662-staged-transfer-inspection-audit.json": [
        "staged-transfer-inspection",
        "fixed_by_inspect_sync_staged_transfer_missing_chunks",
        "fixed_by_post_write_inspection_refactor",
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
        raise AssertionError("missing required rev0662 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0662 package must not carry the rev0661 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0662-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0662-staged-transfer-inspection-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0662-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0662-staged-transfer-inspection-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0662" or audit.get("parent_revision") != "rev0661":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0662 must claim C++ behavior changed")
    required_api = {
        "SyncStagedTransferInspectionOptions added for local_root_path and staging_root_path",
        "SyncStagedTransferInspectionResult added for staged_file_exists, staged_file_complete, receipt counts, content hash, and missing_chunks",
        "inspect_sync_staged_transfer added to inspect receipt-backed staged transfers for resume",
        "write_sync_staged_chunk now reports completion through staged-transfer inspection",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("partial_transfer_resume_had_no_public_inspection_boundary") != "fixed_by_inspect_sync_staged_transfer_missing_chunks":
        raise AssertionError("audit must record staged-transfer inspection fix")
    if findings.get("chunk_write_completion_logic_was_not_shared_with_restart_resume_path") != "fixed_by_post_write_inspection_refactor":
        raise AssertionError("audit must record post-write inspection refactor")
    if findings.get("receipt_tamper_detection_needed_scheduler_facing_api") != "fixed_by_inspection_failing_closed_on_receipt_or_staged_byte_mismatch":
        raise AssertionError("audit must record scheduler-facing tamper detection")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0662-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0662" or manifest.get("parent_revision") != "rev0661":
        raise AssertionError("rev0662 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-staged-transfer-inspection":
        raise AssertionError("rev0662 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0662 product mission tag mismatch")
    if manifest.get("codename") != "staged-transfer-inspection":
        raise AssertionError("rev0662 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0662")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0662 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0661 active binary")
    if "schema/rev0662/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
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
