#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0654" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0654-sync-manifest-diff-audit.json"
ACTIVE_BINARY = "bin/rev0654/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=54 failed=0"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"

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
    "docs/0044-rev0654-sync-manifest-diff.md",
    "audit/rev0654-sync-manifest-diff-audit.json",
    "audit/rev0654-sync-manifest-diff-source.patch",
    "audit/logs/rev0654-release-o0-configure.log",
    "audit/logs/rev0654-release-o0-build.log",
    "audit/logs/rev0654-release-o0-ctest.log",
    "audit/logs/rev0654-sync-manifest-diff-selftest.log",
    "audit/logs/rev0654-asan-ubsan-configure.log",
    "audit/logs/rev0654-asan-ubsan-build.log",
    "audit/logs/rev0654-asan-ubsan-sync-manifest-diff-selftest.log",
    "audit/logs/rev0654-binary-sha256.txt",
    "audit/logs/rev0654-binary-ldd.txt",
    "audit/logs/rev0654-sync-manifest-diff-package-validator.log",
    "tools/validate_rev0654_sync_manifest_diff.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0654 adds `SyncManifestDiffPlan`",
        "build_sync_manifest_diff_plan",
        "publisher-neutral version digests",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0654",
        "SyncManifestDiffPlan",
        "sync_manifest_entry_version_digest",
        "build_sync_manifest_diff_plan",
        "Known ceiling after rev0654",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "enum class SyncPlanAction",
        "enum class SyncLineageRelation",
        "struct SyncManifestPlanEntry",
        "struct SyncManifestDiffPlan",
        "SyncValidationResult build_sync_manifest_diff_plan",
        "std::string sync_manifest_entry_version_digest",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "compare_lineage_vectors",
        "chunks_needed_to_materialize_remote_file",
        "build_sync_manifest_diff_plan",
        "sync_manifest_entry_version_digest",
        "manifest diff compares publisher-neutral version digests",
        "manifest diff requests only chunks unavailable by local hash and length",
        "manifest diff records concurrent vector-clock edits as conflicts",
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
        "made comparable in rev0654",
        "publisher-neutral version digest",
        "manifest/path/index/diff",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0654",
        "deterministic local/remote manifest diff planning",
        "Persist the local manifest/index",
    ],
    "docs/0044-rev0654-sync-manifest-diff.md": [
        "C++ sync manifest diff/planning seam",
        "publisher-bound entry digests",
        "publisher-neutral version digest",
        "Package validator passed",
        "does not persist manifest state",
    ],
    "audit/logs/rev0654-sync-manifest-diff-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0654-asan-ubsan-sync-manifest-diff-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0654-release-o0-ctest.log": [
        EXPECTED_CTEST,
    ],
    "audit/logs/rev0654-sync-manifest-diff-package-validator.log": [
        "rev0654 sync manifest diff package validator passed",
    ],
    "bin/HISTORY.md": [
        "rev0654",
        "manifest diff/planning seam",
        "rev0653 runnable binary is intentionally omitted",
    ],
}

FORBIDDEN_CURRENT_PHRASES = {
    "README.md": [
        "Rev0653 adds `SyncFolderScanOptions`",
        "manifest diff engine, content transfer scheduler",
        "local authorization-and-idempotency evidence kernel",
    ],
    "cpp/anonsync_core/README.md": [
        "# anonsync_core rev0653",
        "Known ceiling after rev0653",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0653",
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
            raise AssertionError(f"required rev0654 file missing: {path}")
    for stale in [
        "bin/rev0653/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "bin/rev0652/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "bin/rev0651/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
    ]:
        if (ROOT / stale).exists():
            raise AssertionError(f"stale runnable binary should not be packaged: {stale}")
    for path, phrases in REQUIRED_PHRASES.items():
        for phrase in phrases:
            assert_contains(path, phrase)
    for path, phrases in FORBIDDEN_CURRENT_PHRASES.items():
        for phrase in phrases:
            assert_not_contains(path, phrase)
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0654" or audit.get("parent_revision") != "rev0653":
        raise AssertionError("audit lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0654 must claim C++ behavior changed")
    findings = audit.get("audit_findings", {})
    if findings.get("publisher_bound_digest_vs_version_identity") != "fixed":
        raise AssertionError("audit must record publisher-bound digest refactor")
    if findings.get("manifest_diff_planning_gap") != "implemented":
        raise AssertionError("audit must record manifest diff planning implementation")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0654-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0654" or manifest.get("parent_revision") != "rev0653":
        raise AssertionError("rev0654 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-sync-manifest-diff":
        raise AssertionError("rev0654 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0654 product mission tag mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0654")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0654 file missing from manifest: {path}")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0654/slim-cube-manifest.json" not in excluded:
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
    print("rev0654 sync manifest diff package validator passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
