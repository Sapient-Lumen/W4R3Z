#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0656" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0656-verified-stage-rename-audit.json"
ACTIVE_BINARY = "bin/rev0656/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0655/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=71 failed=0"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_VALIDATOR = "rev0656 verified stage rename package validator passed"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "bin/HISTORY.md",
    ACTIVE_BINARY,
    "cpp/anonsync_core/CMakeLists.txt",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/anonsync_core.cpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0046-rev0656-verified-stage-rename.md",
    "audit/rev0656-verified-stage-rename-audit.json",
    "audit/rev0656-verified-stage-rename-source.patch",
    "audit/logs/rev0656-release-o0-configure.log",
    "audit/logs/rev0656-release-o0-build.log",
    "audit/logs/rev0656-release-o0-ctest.log",
    "audit/logs/rev0656-staged-file-materialization-selftest.log",
    "audit/logs/rev0656-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0656-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0656-binary-sha256.txt",
    "audit/logs/rev0656-binary-ldd.txt",
    "audit/logs/rev0656-verified-stage-rename-package-validator.log",
    "tools/validate_rev0656_verified_stage_rename.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0656 adds `SyncStagedFileMaterializationOptions`",
        "materialize_staged_sync_file",
        "sync-materialize:v1:",
        "rejects existing symlink ancestors",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0656",
        "SyncStagedFileMaterializationResult",
        "materialize_staged_sync_file",
        "complete-file materialization only",
        "peer chunk receipt and partial-transfer state are still future work",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncStagedFileMaterializationOptions",
        "struct SyncStagedFileMaterializationResult",
        "materialize_staged_sync_file",
        "materialized = false",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "require_no_symlink_ancestors_under_root_or_throw",
        "verify_staged_file_matches_entry_or_throw",
        "fsync_file_if_supported_or_throw",
        "materialize_staged_sync_file",
        "sync-materialize:v1:",
        "staged file materialization rejects hash-mismatched staging files without committing target bytes",
        "local apply plan rejects existing symlink ancestors below the synchronized root",
    ],
    "docs/0046-rev0656-verified-stage-rename.md": [
        "C++ verified staged-file materialization",
        "StageRemoteFile",
        "fsyncs where supported",
        "symlink ancestors",
        "does not implement chunk receipt from a peer",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "verified staged-file materialization",
        "materialize_staged_sync_file",
        "partial chunk receipt/write accounting",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0656",
        "verified complete-file materialization",
        "chunk receipt/write accounting",
        "conflict-copy materialization",
    ],
    "bin/HISTORY.md": [
        "rev0656",
        "verified staged-file materialization seam",
        "rev0655: historical source/audit only",
    ],
    "audit/rev0656-verified-stage-rename-audit.json": [
        "verified-stage-rename",
        "fixed_with_existing_symlink_ancestor_rejection",
        "sync-materialize:v1",
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
        raise AssertionError("missing required rev0656 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0656 package must not carry the rev0655 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0656-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0656-staged-file-materialization-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0656-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow ASAN/UBSAN selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0656-verified-stage-rename-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0656" or audit.get("parent_revision") != "rev0655":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0656 must claim C++ behavior changed")
    api = set(audit.get("cxx_api_added", []))
    for name in ["SyncStagedFileMaterializationOptions", "SyncStagedFileMaterializationResult", "materialize_staged_sync_file"]:
        if name not in api:
            raise AssertionError(f"audit missing API addition: {name}")
    findings = audit.get("audit_findings", {})
    if findings.get("lexical_path_only_apply_planning") != "fixed_with_existing_symlink_ancestor_rejection":
        raise AssertionError("audit must record symlink-ancestor apply planning fix")
    if findings.get("stage_remote_file_no_verified_commit") != "fixed_for_complete_staged_files":
        raise AssertionError("audit must record staged-file materialization fix")
    if findings.get("tampered_staging_commit_risk") != "rejected_before_rename":
        raise AssertionError("audit must record tampered staging rejection")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow sanitizer selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0656-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0656" or manifest.get("parent_revision") != "rev0655":
        raise AssertionError("rev0656 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-verified-stage-rename":
        raise AssertionError("rev0656 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0656 product mission tag mismatch")
    if manifest.get("codename") != "verified-stage-rename":
        raise AssertionError("rev0656 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0656")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0656 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0655 active binary")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0656/slim-cube-manifest.json" not in excluded:
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
