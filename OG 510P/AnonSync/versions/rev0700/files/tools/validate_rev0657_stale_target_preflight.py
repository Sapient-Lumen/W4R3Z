#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0657" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0657-stale-target-preflight-audit.json"
ACTIVE_BINARY = "bin/rev0657/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0656/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=80 failed=0"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_VALIDATOR = "rev0657 stale target preflight package validator passed"

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
    "docs/0047-rev0657-stale-target-preflight.md",
    "audit/rev0657-stale-target-preflight-audit.json",
    "audit/rev0657-stale-target-preflight-source.patch",
    "audit/logs/rev0657-release-configure.log",
    "audit/logs/rev0657-release-build.log",
    "audit/logs/rev0657-release-ctest.log",
    "audit/logs/rev0657-stale-target-preflight-selftest.log",
    "audit/logs/rev0657-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0657-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0657-binary-sha256.txt",
    "audit/logs/rev0657-binary-ldd.txt",
    "audit/logs/rev0657-stale-target-preflight-package-validator.log",
    "tools/validate_rev0657_stale_target_preflight.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0657",
        "stale-target overwrite preflight",
        "sync-local-apply:v1:",
        "preflight_checked_target",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0657",
        "local/remote size and content-hash evidence",
        "materialize_staged_sync_file",
        "stale-target preflight",
        "peer chunk receipt and partial-transfer state are future work",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "std::uint64_t local_size_bytes = 0;",
        "std::string local_content_sha256;",
        "bool local_entry_present = false;",
        "bool preflight_checked_target = false;",
        "bool replaced_existing_target = false;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "preflight_materialization_target_state",
        "staged file materialization target changed after local manifest planning",
        "staged file materialization target appeared after remote-only or tombstone-based planning",
        "manifest diff carries local and remote content evidence for overwrite preflight",
        "local apply plan preserves local content evidence for stale-overwrite checks",
        "staged file materialization rejects stale local targets before overwrite",
        "staged file materialization rejects newly appeared local targets for remote-only plans",
    ],
    "docs/0047-rev0657-stale-target-preflight.md": [
        "C++ stale-target preflight before staged-file rename",
        "stale local overwrite gap",
        "remote-only plan requires absence",
        "current target size and SHA-256",
        "does not implement peer chunk receipt",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "stale-target overwrite preflight",
        "rev0657",
        "partial chunk receipt/write accounting",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0657",
        "stale-target overwrite preflight",
        "chunk receipt/write accounting",
        "conflict-copy materialization",
    ],
    "bin/HISTORY.md": [
        "rev0657",
        "stale-target preflight seam",
        "rev0656: historical source/audit only",
    ],
    "audit/rev0657-stale-target-preflight-audit.json": [
        "stale-target-preflight",
        "fixed_for_StageRemoteFile_by_target_content_preflight",
        "sync-local-apply:v1",
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
        raise AssertionError("missing required rev0657 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0657 package must not carry the rev0656 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0657-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0657-stale-target-preflight-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0657-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow ASAN/UBSAN selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0657-stale-target-preflight-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0657" or audit.get("parent_revision") != "rev0656":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0657 must claim C++ behavior changed")
    api = set(audit.get("cxx_api_changed", []))
    required_api_phrases = [
        "SyncManifestPlanEntry carries local/remote size and content SHA-256 evidence",
        "SyncLocalApplyPlanEntry carries local/remote presence, kind, size, and content SHA-256 evidence",
        "SyncStagedFileMaterializationResult carries preflight_checked_target and replaced_existing_target flags",
    ]
    for phrase in required_api_phrases:
        if phrase not in api:
            raise AssertionError(f"audit missing API change: {phrase}")
    findings = audit.get("audit_findings", {})
    if findings.get("rev0656_staged_file_valid_but_target_may_be_stale") != "fixed_for_StageRemoteFile_by_target_content_preflight":
        raise AssertionError("audit must record stale-target preflight fix")
    if findings.get("apply_intent_did_not_bind_local_content_preconditions") != "fixed_by_carrying_presence_kind_size_content_evidence_and_key_binding":
        raise AssertionError("audit must record apply intent evidence binding fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow sanitizer selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0657-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0657" or manifest.get("parent_revision") != "rev0656":
        raise AssertionError("rev0657 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-stale-target-preflight":
        raise AssertionError("rev0657 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0657 product mission tag mismatch")
    if manifest.get("codename") != "stale-target-preflight":
        raise AssertionError("rev0657 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0657")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0657 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0656 active binary")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0657/slim-cube-manifest.json" not in excluded:
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
