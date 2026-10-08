#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0658 remote tombstone application package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=92 failed=0"
ACTIVE_BINARY = "bin/rev0658/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0657/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0658-remote-tombstone-apply-audit.json"
MANIFEST = ROOT / "schema/rev0658/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0048-rev0658-remote-tombstone-apply.md",
    "audit/rev0658-remote-tombstone-apply-audit.json",
    "audit/rev0658-remote-tombstone-apply-source.patch",
    "audit/logs/rev0658-release-configure.log",
    "audit/logs/rev0658-release-build.log",
    "audit/logs/rev0658-release-ctest.log",
    "audit/logs/rev0658-remote-tombstone-apply-selftest.log",
    "audit/logs/rev0658-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0658-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0658-binary-sha256.txt",
    "audit/logs/rev0658-binary-ldd.txt",
    "audit/logs/rev0658-remote-tombstone-apply-package-validator.log",
    "tools/validate_rev0658_remote_tombstone_apply.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0658",
        "apply_sync_remote_tombstone",
        "sync-tombstone:v1:",
        "remote tombstone application",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0658",
        "SyncTombstoneApplicationOptions",
        "SyncTombstoneApplicationResult",
        "apply_sync_remote_tombstone",
        "peer chunk receipt and partial-transfer state are future work",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncTombstoneApplicationOptions",
        "struct SyncTombstoneApplicationResult",
        "bool target_existed = false;",
        "SyncValidationResult apply_sync_remote_tombstone",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "tombstone_application_idempotency_key",
        "preflight_tombstone_target_state",
        "remote tombstone application target changed after local manifest planning",
        "apply_sync_remote_tombstone",
        "sync-tombstone:v1:",
        "remote tombstone application verifies planned local bytes before deleting the file",
        "remote tombstone application rejects stale changed targets before deleting",
        "remote tombstone application rejects newly appeared targets for remote-only tombstone plans",
    ],
    "docs/0048-rev0658-remote-tombstone-apply.md": [
        "C++ remote tombstone application",
        "DeleteLocalPath",
        "regular file whose size and SHA-256 match the planned local evidence",
        "sync-tombstone:v1:",
        "does not implement peer chunk receipt",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "remote tombstone application",
        "rev0658",
        "apply_sync_remote_tombstone",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0658",
        "safe remote tombstone application",
        "PreserveConflictCopy",
        "chunk receipt/write accounting",
    ],
    "bin/HISTORY.md": [
        "rev0658",
        "remote tombstone application seam",
        "rev0657: historical source/audit only",
    ],
    "audit/rev0658-remote-tombstone-apply-audit.json": [
        "remote-tombstone-apply",
        "fixed_for_regular_files_by_apply_sync_remote_tombstone",
        "sync-tombstone:v1",
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
        raise AssertionError("missing required rev0658 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0658 package must not carry the rev0657 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0658-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0658-remote-tombstone-apply-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0658-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow ASAN/UBSAN selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0658-remote-tombstone-apply-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0658" or audit.get("parent_revision") != "rev0657":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0658 must claim C++ behavior changed")
    api = set(audit.get("cxx_api_changed", []))
    required_api = {
        "SyncTombstoneApplicationOptions carries the local root for remote tombstone application",
        "SyncTombstoneApplicationResult carries target path, sync-tombstone:v1 idempotency evidence, preflight_checked_target, target_existed, and removed flags",
        "apply_sync_remote_tombstone executes ApplyRemoteTombstone/DeleteLocalPath apply entries after remote digest/version and stale-target preflight",
    }
    missing_api = required_api - api
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("rev0657_delete_local_path_was_planner_only") != "fixed_for_regular_files_by_apply_sync_remote_tombstone":
        raise AssertionError("audit must record planner-only tombstone execution fix")
    if findings.get("remote_tombstone_could_delete_stale_or_appeared_target_without_boundary") != "fixed_by_size_sha256_absence_preflight_before_remove":
        raise AssertionError("audit must record tombstone stale-target preflight fix")
    if findings.get("delete_evidence_lacked_commit_namespace") != "fixed_by_sync_tombstone_v1_idempotency_key":
        raise AssertionError("audit must record tombstone idempotency namespace fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow sanitizer selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0658-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0658" or manifest.get("parent_revision") != "rev0657":
        raise AssertionError("rev0658 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-remote-tombstone-apply":
        raise AssertionError("rev0658 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0658 product mission tag mismatch")
    if manifest.get("codename") != "remote-tombstone-apply":
        raise AssertionError("rev0658 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0658")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0658 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0657 active binary")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0658/slim-cube-manifest.json" not in excluded:
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
