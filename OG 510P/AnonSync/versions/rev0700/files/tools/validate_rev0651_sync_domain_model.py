#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0651" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0651-sync-domain-model-audit.json"
ACTIVE_BINARY = "bin/rev0651/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"

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
    "docs/0041-rev0651-sync-domain-model.md",
    "audit/rev0651-sync-domain-model-audit.json",
    "audit/rev0651-sync-domain-model-source.patch",
    "audit/logs/rev0651-release-o0-configure.log",
    "audit/logs/rev0651-release-o0-build.log",
    "audit/logs/rev0651-release-o0-ctest.log",
    "audit/logs/rev0651-sync-domain-model-selftest.log",
    "audit/logs/rev0651-asan-ubsan-configure.log",
    "audit/logs/rev0651-asan-ubsan-build.log",
    "audit/logs/rev0651-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0651-binary-sha256.txt",
    "audit/logs/rev0651-binary-ldd.txt",
    "tools/validate_rev0651_sync_domain_model.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0651 is the first code-bearing turn after the mission correction",
        "portable relative path normalization",
        "sync-scoped mutation idempotency keys",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "Rev0651 adds the first concrete sync-domain module",
        "NormalizedSyncPath",
        "validate_sync_manifest_entry",
        "sync_mutation_idempotency_key",
        "--selftest-sync-domain-model",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncManifestEntry",
        "SyncValidationResult normalize_sync_relative_path",
        "std::string sync_mutation_idempotency_key",
        "int run_sync_domain_model_selftest();",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "bool valid_utf8",
        "reserved_windows_device_name",
        "validate_sync_manifest_entry",
        "anonsync-sync-manifest-entry-v1",
        "generic_effect",
    ],
    "cpp/anonsync_core/src/anonsync_core.cpp": [
        "--selftest-sync-domain-model",
        "run_sync_domain_model_selftest",
    ],
    "cpp/anonsync_core/CMakeLists.txt": [
        "src/sync_domain.cpp",
        "anonsync_core_sync_domain_model_selftest",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Started in rev0651",
        "New sync behavior should be split by domain",
    ],
    "docs/0003-next-risk-register.md": [
        "Rev0651 added portable relative paths",
        "Build a deterministic local folder/index harness",
    ],
    "docs/0041-rev0651-sync-domain-model.md": [
        "portable relative sync paths",
        "Idempotency boundary",
        "Package validator passed",
        "does not scan folders",
    ],
    "audit/logs/rev0651-sync-domain-model-selftest.log": [
        "anonsync_core sync domain model selftest passed=18 failed=0",
    ],
    "audit/logs/rev0651-asan-ubsan-sync-domain-selftest.log": [
        "anonsync_core sync domain model selftest passed=18 failed=0",
    ],
    "audit/logs/rev0651-release-o0-ctest.log": [
        "100% tests passed, 0 tests failed out of 27",
    ],
    "bin/HISTORY.md": [
        "rev0651",
        "--selftest-sync-domain-model",
    ],
}

FORBIDDEN_CURRENT_PHRASES = {
    "README.md": [
        "Rev0650 is a mission correction only",
        "local authorization-and-idempotency evidence kernel",
        "not anonymity, synchronization",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text(path: str) -> str:
    return (ROOT / path).read_text(errors="replace")


def assert_contains(path: str, phrase: str) -> None:
    if phrase not in text(path):
        raise AssertionError(f"missing required phrase in {path!r}: {phrase!r}")


def assert_not_contains(path: str, phrase: str) -> None:
    if phrase in text(path):
        raise AssertionError(f"forbidden stale phrase in {path!r}: {phrase!r}")


def assert_docs_and_code() -> None:
    for path in REQUIRED_CURRENT_FILES:
        if not (ROOT / path).exists():
            raise AssertionError(f"required rev0651 file missing: {path}")
    for path, phrases in REQUIRED_PHRASES.items():
        for phrase in phrases:
            assert_contains(path, phrase)
    for path, phrases in FORBIDDEN_CURRENT_PHRASES.items():
        for phrase in phrases:
            assert_not_contains(path, phrase)
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0651" or audit.get("parent_revision") != "rev0650":
        raise AssertionError("audit lineage mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0651 must claim C++ behavior changed")
    if audit.get("refactor_scope") != "Introduces a separate sync_domain.cpp translation unit instead of growing runner.cpp/sqlite_replay_ledger.cpp/reporting_selftests.cpp.":
        raise AssertionError("audit refactor scope mismatch")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != "100% tests passed, 0 tests failed out of 27":
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != "anonsync_core sync domain model selftest passed=18 failed=0":
        raise AssertionError("audit sync-domain selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0651-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0651" or manifest.get("parent_revision") != "rev0650":
        raise AssertionError("rev0651 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-sync-domain-manifest":
        raise AssertionError("rev0651 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0651 product mission tag mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0651")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0651 file missing from manifest: {path}")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0651/slim-cube-manifest.json" not in excluded:
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
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("active binary sha not bound in manifest")


def main() -> int:
    assert_docs_and_code()
    assert_binary_sha()
    assert_manifest()
    print("rev0651 sync-domain model validator passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
