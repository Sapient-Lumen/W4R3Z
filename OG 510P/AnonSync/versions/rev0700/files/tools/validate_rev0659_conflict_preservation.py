#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0659 conflict preservation package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=103 failed=0"
ACTIVE_BINARY = "bin/rev0659/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0658/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0659-conflict-preservation-audit.json"
MANIFEST = ROOT / "schema/rev0659/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0049-rev0659-conflict-preservation.md",
    "audit/rev0659-conflict-preservation-audit.json",
    "audit/rev0659-conflict-preservation-source.patch",
    "audit/logs/rev0659-release-configure.log",
    "audit/logs/rev0659-release-build.log",
    "audit/logs/rev0659-release-ctest.log",
    "audit/logs/rev0659-conflict-preservation-selftest.log",
    "audit/logs/rev0659-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0659-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0659-binary-sha256.txt",
    "audit/logs/rev0659-binary-ldd.txt",
    "audit/logs/rev0659-conflict-preservation-package-validator.log",
    "tools/validate_rev0659_conflict_preservation.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0659",
        "apply_sync_conflict_preservation",
        "sync-conflict:v1:",
        "PreserveConflictCopy",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0659",
        "SyncConflictPreservationOptions",
        "SyncConflictPreservationResult",
        "apply_sync_conflict_preservation",
        "Local tombstone vs remote file conflict semantics",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncConflictPreservationOptions",
        "struct SyncConflictPreservationResult",
        "bool conflict_copy_preserved = false;",
        "SyncValidationResult apply_sync_conflict_preservation",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "conflict_preservation_idempotency_key",
        "preflight_conflict_target_state",
        "ensure_conflict_copy_absent_or_matching",
        "apply_sync_conflict_preservation",
        "sync-conflict:v1:",
        "conflict preservation copies local bytes and materializes verified remote conflict bytes",
        "conflict preservation rejects stale local targets before copying or promoting remote bytes",
        "conflict preservation copies local bytes and applies the conflicting remote tombstone",
        "entry.remote_entry_present && entry.remote_entry_kind == SyncManifestEntryKind::File",
    ],
    "docs/0049-rev0659-conflict-preservation.md": [
        "C++ conflict-copy preservation",
        "PreserveConflictCopy",
        "sync-conflict:v1:",
        "file/delete conflict apply plans no longer fail shape validation",
        "does not implement peer chunk receipt",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "conflict-copy preservation",
        "rev0659",
        "apply_sync_conflict_preservation",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0659",
        "conflict-copy preservation",
        "local-tombstone conflict semantics",
        "chunk receipt/write accounting",
    ],
    "bin/HISTORY.md": [
        "rev0659",
        "conflict preservation seam",
        "rev0658: historical source/audit only",
    ],
    "audit/rev0659-conflict-preservation-audit.json": [
        "conflict-preservation",
        "fixed_by_remote_kind_specific_staging_validation",
        "sync-conflict:v1",
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
        raise AssertionError("missing required rev0659 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0659 package must not carry the rev0658 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0659-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0659-conflict-preservation-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0659-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow ASAN/UBSAN selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0659-conflict-preservation-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0659" or audit.get("parent_revision") != "rev0658":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0659 must claim C++ behavior changed")
    api = set(audit.get("cxx_api_changed", []))
    required_api = {
        "SyncConflictPreservationOptions carries local and staging roots for conflict preservation",
        "SyncConflictPreservationResult carries target, staging, conflict-copy, sync-conflict:v1 evidence, and remote outcome fields",
        "apply_sync_conflict_preservation executes RecordConflict/PreserveConflictCopy apply entries for planned regular local files",
    }
    missing_api = required_api - api
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("rev0655_preserve_conflict_copy_was_planner_only") != "fixed_for_regular_local_files_by_apply_sync_conflict_preservation":
        raise AssertionError("audit must record planner-only conflict preservation fix")
    if findings.get("file_delete_conflicts_were_forced_to_stage_remote_content") != "fixed_by_remote_kind_specific_staging_validation":
        raise AssertionError("audit must record file/delete conflict validator fix")
    if findings.get("conflict_evidence_lacked_commit_namespace") != "fixed_by_sync_conflict_v1_idempotency_key":
        raise AssertionError("audit must record sync-conflict idempotency namespace fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow sanitizer selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0659-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0659" or manifest.get("parent_revision") != "rev0658":
        raise AssertionError("rev0659 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-conflict-preservation":
        raise AssertionError("rev0659 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0659 product mission tag mismatch")
    if manifest.get("codename") != "conflict-preservation":
        raise AssertionError("rev0659 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0659")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0659 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0658 active binary")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0659/slim-cube-manifest.json" not in excluded:
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
