#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0660 chunk receipt resume package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=121 failed=0"
ACTIVE_BINARY = "bin/rev0660/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0659/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0660-chunk-receipt-resume-audit.json"
MANIFEST = ROOT / "schema/rev0660/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0050-rev0660-chunk-receipt-resume.md",
    "audit/rev0660-chunk-receipt-resume-audit.json",
    "audit/rev0660-chunk-receipt-resume-source.patch",
    "audit/logs/rev0660-release-configure.log",
    "audit/logs/rev0660-release-build.log",
    "audit/logs/rev0660-release-ctest.log",
    "audit/logs/rev0660-chunk-receipt-resume-selftest.log",
    "audit/logs/rev0660-binary-sha256.txt",
    "audit/logs/rev0660-binary-ldd.txt",
    "audit/logs/rev0660-chunk-receipt-resume-package-validator.log",
    "tools/validate_rev0660_chunk_receipt_resume.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0660",
        "write_sync_staged_chunk",
        "sync-chunk-receipt:v1:",
        "receipt-backed staged chunk writes",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0660",
        "SyncChunkReceiptWriteOptions",
        "SyncChunkReceiptWriteResult",
        "write_sync_staged_chunk",
        "sync-chunk-receipt:v1:",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncChunkReceiptWriteOptions",
        "struct SyncChunkReceiptWriteResult",
        "bool staged_file_complete = false;",
        "SyncValidationResult write_sync_staged_chunk",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "chunk_receipt_material",
        "staged_chunk_receipt_idempotency_key",
        "write_sync_staged_chunk",
        "sync-chunk-receipt:v1:",
        "receipt_file_exists_matching_or_throw",
        "verify_staged_file_complete_with_receipts_or_throw",
        "staged chunk write records a receipt without committing an incomplete remote file",
        "staged chunk write resumes by reusing an existing matching receipt",
        "staged chunk write declares completion only after all receipts and staged bytes verify",
        "staged chunk write does not treat an all-zero sparse hole or missing file as complete without bytes",
    ],
    "docs/0050-rev0660-chunk-receipt-resume.md": [
        "C++ staged chunk receipt/resume",
        "write_sync_staged_chunk",
        "sync-chunk-receipt:v1:",
        "sparse holes",
        "does not persist transfer state",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "receipt-backed staged chunk writes in rev0660",
        "write_sync_staged_chunk",
        "chunk receipt/write accounting",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0660",
        "sync-chunk-receipt:v1:",
        "receipt garbage collection after materialization",
    ],
    "bin/HISTORY.md": [
        "rev0660",
        "staged chunk receipt/resume seam",
        "rev0659: historical source/audit only",
    ],
    "audit/rev0660-chunk-receipt-resume-audit.json": [
        "chunk-receipt-resume",
        "fixed_by_write_sync_staged_chunk_receipts",
        "sync-chunk-receipt:v1",
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
        raise AssertionError("missing required rev0660 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0660 package must not carry the rev0659 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0660-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0660-chunk-receipt-resume-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0660-chunk-receipt-resume-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0660" or audit.get("parent_revision") != "rev0659":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0660 must claim C++ behavior changed")
    api = set(audit.get("cxx_api_changed", []))
    required_api = {
        "SyncChunkReceiptWriteOptions carries local and staging roots for receipt-backed staged chunk writes",
        "SyncChunkReceiptWriteResult carries staging path, receipt path, chunk evidence, sync-chunk-receipt:v1 idempotency evidence, reuse/write flags, and completion evidence",
        "write_sync_staged_chunk verifies and records one remote manifest chunk for StageRemoteFile or remote-file PreserveConflictCopy apply entries",
    }
    missing_api = required_api - api
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("complete_staged_file_was_out_of_band_before_rev0660") != "fixed_by_write_sync_staged_chunk_receipts":
        raise AssertionError("audit must record out-of-band staged-file fix")
    if findings.get("partial_transfer_resume_lacked_durable_chunk_evidence") != "fixed_by_deterministic_staging_root_receipt_files":
        raise AssertionError("audit must record durable receipt evidence")
    if findings.get("sparse_or_all_zero_holes_could_not_be_distinguished_from_received_chunks") != "fixed_by_requiring_per_chunk_receipts_before_completion":
        raise AssertionError("audit must record sparse/all-zero hole fix")
    if findings.get("receipt_reuse_needed_byte_reverification") != "fixed_by_rehashing_existing_staged_ranges_before_reuse":
        raise AssertionError("audit must record receipt reuse byte verification")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0660-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0660" or manifest.get("parent_revision") != "rev0659":
        raise AssertionError("rev0660 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-chunk-receipt-resume":
        raise AssertionError("rev0660 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0660 product mission tag mismatch")
    if manifest.get("codename") != "chunk-receipt-resume":
        raise AssertionError("rev0660 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0660")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0660 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0659 active binary")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0660/slim-cube-manifest.json" not in excluded:
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
