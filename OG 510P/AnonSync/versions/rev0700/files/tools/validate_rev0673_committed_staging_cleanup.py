#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0673 committed staging cleanup package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=197 failed=0"
ACTIVE_BINARY = "bin/rev0673/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0672/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0673-committed-staging-cleanup-audit.json"
MANIFEST = ROOT / "schema/rev0673/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0673-committed-staging-cleanup-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0673/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0063-rev0673-committed-staging-cleanup.md",
    "audit/rev0673-committed-staging-cleanup-audit.json",
    "audit/rev0673-committed-staging-cleanup-source.patch",
    "audit/logs/rev0673-release-o0-configure.log",
    "audit/logs/rev0673-release-o0-build.log",
    "audit/logs/rev0673-release-o0-ctest.log",
    "audit/logs/rev0673-committed-staging-cleanup-selftest.log",
    "audit/logs/rev0673-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0673-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0673-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0673-binary-sha256.txt",
    "audit/logs/rev0673-binary-ldd.txt",
    "tools/validate_rev0673_committed_staging_cleanup.py",
    "schema/rev0673/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0673",
        "committed staging cleanup",
        "cleanup_sync_staged_transfer_artifacts",
        "SyncStagedTransferCleanupOptions",
        "SyncStagedTransferCleanupResult",
        "cleanup_staged_transfer_artifacts_after_materialization",
        "anonsync_core sync domain model selftest passed=197 failed=0",
        "It does not persist session state, model cleanup checkpoints in SQLite",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0673",
        "SyncStagedTransferCleanupOptions",
        "SyncStagedTransferCleanupResult",
        "cleanup_sync_staged_transfer_artifacts",
        "committed `.part.chunks` receipt sidecars",
        "staging root must be empty after convergence",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncStagedTransferCleanupOptions",
        "struct SyncStagedTransferCleanupResult",
        "bool cleanup_staged_transfer_artifacts_after_materialization = true;",
        "bool staging_artifacts_cleaned = false;",
        "std::uint64_t cleanup_receipts_removed = 0;",
        "cleanup_sync_staged_transfer_artifacts",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "staged_transfer_cleanup_idempotency_key",
        "prune_empty_parent_directories_up_to_root_or_throw",
        "SyncValidationResult cleanup_sync_staged_transfer_artifacts",
        "staged transfer cleanup refuses to remove artifacts while the staging file still exists",
        "staged transfer cleanup terminal target does not match remote content evidence",
        "fake peer file-fetch session staged artifact cleanup failed",
        "fake peer file-fetch session cleans committed staging receipts and prunes empty staging directories",
    ],
    "docs/0063-rev0673-committed-staging-cleanup.md": [
        "Rev0673 — committed staging cleanup",
        "cleanup_sync_staged_transfer_artifacts",
        "Audit/refactor performed",
        "committed staging cleanup",
        "anonsync_core sync domain model selftest passed=197 failed=0",
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0673 product slice — committed staging cleanup",
        "cleanup_sync_staged_transfer_artifacts",
        "anonsync_core sync domain model selftest passed=197 failed=0",
        "100% tests passed, 0 tests failed out of 27",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0673",
        "Rev0673 priority note",
        "cleanup checkpoints",
        "abandoned or in-progress",
    ],
    "bin/HISTORY.md": [
        "rev0673",
        "committed staged-transfer cleanup",
        "rev0672: historical source/audit only",
    ],
    "audit/rev0673-committed-staging-cleanup-audit.json": [
        "committed-staging-cleanup",
        "cleanup_sync_staged_transfer_artifacts",
        "No durable SQLite session state or cleanup checkpoints yet",
        "package_validator_summary",
    ],
    "audit/rev0673-committed-staging-cleanup-source.patch": [
        "0063-rev0673-committed-staging-cleanup.md",
        "SyncStagedTransferCleanupOptions",
        "cleanup_sync_staged_transfer_artifacts",
        "validate_rev0673_committed_staging_cleanup.py",
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
        raise AssertionError("missing required rev0673 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0673 package must not carry the rev0672 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0673-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0673-committed-staging-cleanup-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0673-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0673-release-o0-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0673" or audit.get("parent_revision") != "rev0672":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "committed-staging-cleanup":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0673 must claim C++ behavior changed")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_o0_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0673-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0673" or manifest.get("parent_revision") != "rev0672":
        raise AssertionError("rev0673 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-committed-staging-cleanup":
        raise AssertionError("rev0673 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0673 product mission tag mismatch")
    if manifest.get("codename") != "committed-staging-cleanup":
        raise AssertionError("rev0673 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0673")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    if set(manifest.get("excluded_mutable_evidence", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest excluded mutable evidence mismatch")

    expected_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED_MUTABLE:
            continue
        expected_files.append(rel)
    expected_files.sort()

    rows = manifest.get("files", [])
    files = {item.get("path"): item for item in rows}
    if manifest.get("file_count") != len(expected_files) or len(rows) != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    if set(files) != set(expected_files):
        missing = sorted(set(expected_files) - set(files))[:12]
        extra = sorted(set(files) - set(expected_files))[:12]
        raise AssertionError(f"manifest path set mismatch missing={missing} extra={extra}")
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0672 active binary")
    for rel in expected_files:
        row = files[rel]
        path = ROOT / rel
        if row.get("size_bytes") != path.stat().st_size:
            raise AssertionError(f"manifest size mismatch for {rel}")
        if row.get("sha256") != sha_file(path):
            raise AssertionError(f"manifest sha mismatch for {rel}")


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_binary_hash()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
