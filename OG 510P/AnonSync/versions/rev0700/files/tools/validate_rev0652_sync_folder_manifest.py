#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0652" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0652-sync-folder-manifest-audit.json"
ACTIVE_BINARY = "bin/rev0652/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=26 failed=0"
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
    "docs/0042-rev0652-sync-folder-manifest.md",
    "audit/rev0652-sync-folder-manifest-audit.json",
    "audit/rev0652-sync-folder-manifest-source.patch",
    "audit/logs/rev0652-release-o0-configure.log",
    "audit/logs/rev0652-release-o0-build.log",
    "audit/logs/rev0652-release-o0-ctest.log",
    "audit/logs/rev0652-sync-domain-manifest-selftest.log",
    "audit/logs/rev0652-asan-ubsan-configure.log",
    "audit/logs/rev0652-asan-ubsan-build.log",
    "audit/logs/rev0652-asan-ubsan-sync-domain-manifest-selftest.log",
    "audit/logs/rev0652-binary-sha256.txt",
    "audit/logs/rev0652-binary-ldd.txt",
    "tools/validate_rev0652_sync_folder_manifest.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0652 deepens the sync-domain seam",
        "SyncFolderManifest",
        "overlong two-byte path validation gap",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0652",
        "SyncFolderManifest",
        "validate_sync_folder_manifest",
        "sync_folder_manifest_digest",
        "overlong two-byte encodings",
        "IngressReservationResult reserve_ingress_request_json",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncFolderManifest",
        "SyncValidationResult validate_sync_folder_manifest",
        "std::string sync_folder_manifest_digest",
        "int run_sync_domain_model_selftest();",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "if (c < 0xc2) return false",
        "std::string digest_manifest_entries",
        "validate_sync_folder_manifest",
        "anonsync-sync-folder-manifest-v1",
        "duplicate manifest path rejected",
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
        "extended in rev0652",
        "folder manifest",
        "New sync behavior should be split by domain",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0652",
        "whole folder manifests",
        "SyncFolderManifest",
    ],
    "docs/0042-rev0652-sync-folder-manifest.md": [
        "C++ sync folder-manifest seam",
        "overlong two-byte sequences",
        "sorted by unique canonical path",
        "Package validator passed",
        "does not scan real folders",
    ],
    "audit/logs/rev0652-sync-domain-manifest-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0652-asan-ubsan-sync-domain-manifest-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0652-release-o0-ctest.log": [
        EXPECTED_CTEST,
    ],
    "bin/HISTORY.md": [
        "rev0652",
        "folder-manifest seam",
        "rev0651 runnable binary is intentionally omitted",
    ],
}

FORBIDDEN_CURRENT_PHRASES = {
    "README.md": [
        "rev0651 is the first code-bearing turn",
        "local authorization-and-idempotency evidence kernel",
        "not anonymity, synchronization",
    ],
    "cpp/anonsync_core/README.md": [
        "# anonsync_core rev0651",
        "IngressReservationServiceResult reserve_ingress_request_json",
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
            raise AssertionError(f"required rev0652 file missing: {path}")
    if (ROOT / "bin/rev0651/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3").exists():
        raise AssertionError("stale rev0651 runnable binary should not be packaged")
    for path, phrases in REQUIRED_PHRASES.items():
        for phrase in phrases:
            assert_contains(path, phrase)
    for path, phrases in FORBIDDEN_CURRENT_PHRASES.items():
        for phrase in phrases:
            assert_not_contains(path, phrase)
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0652" or audit.get("parent_revision") != "rev0651":
        raise AssertionError("audit lineage mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0652 must claim C++ behavior changed")
    if audit.get("audit_findings", {}).get("utf8_overlong_two_byte_gap") != "fixed":
        raise AssertionError("audit must record the UTF-8 overlong fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0652-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0652" or manifest.get("parent_revision") != "rev0651":
        raise AssertionError("rev0652 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-sync-folder-manifest":
        raise AssertionError("rev0652 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0652 product mission tag mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0652")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0652 file missing from manifest: {path}")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0652/slim-cube-manifest.json" not in excluded:
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
    print("rev0652 sync folder-manifest validator passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
