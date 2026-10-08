#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0683 materialize resume executor package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=226 failed=0"
ACTIVE_BINARY = "bin/rev0683/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0682/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0683-materialize-resume-executor-audit.json"
MANIFEST = ROOT / "schema/rev0683/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0683-materialize-resume-executor-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0683/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0073-rev0683-materialize-resume-executor.md",
    "audit/rev0683-materialize-resume-executor-audit.json",
    "audit/rev0683-materialize-resume-executor-source.patch",
    "audit/logs/rev0683-release-configure.log",
    "audit/logs/rev0683-release-build.log",
    "audit/logs/rev0683-release-ctest.log",
    "audit/logs/rev0683-materialize-resume-selftest.log",
    "audit/logs/rev0683-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0683-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0683-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0683-binary-sha256.txt",
    "audit/logs/rev0683-binary-ldd.txt",
    "tools/validate_rev0683_materialize_resume_executor.py",
    "schema/rev0683/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0683",
        "MaterializeStagedFile resume executor",
        "execute_sync_session_checkpoint_resume_materializations",
        "plan_sync_session_checkpoint_resume_actions",
        EXPECTED_SELFTEST,
        "CleanupCommittedStaging",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0683",
        "MaterializeStagedFile resume executor",
        "SyncSessionCheckpointMaterializeResumeResult",
        "execute_sync_session_checkpoint_resume_materializations",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncSessionCheckpointMaterializeResumeOptions",
        "struct SyncSessionCheckpointMaterializeResumeFileResult",
        "struct SyncSessionCheckpointMaterializeResumeResult",
        "SyncValidationResult execute_sync_session_checkpoint_resume_materializations",
        "std::uint64_t post_cleanup_committed_staging_files = 0;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "execute_sync_session_checkpoint_resume_materializations",
        "sync session checkpoint resume materialization executor performs only the complete MaterializeStagedFile branch",
        "sync session checkpoint resume materialization executor transitions the file into cleanup-committed-staging restart state",
        "checkpoint_resume_materialization_idempotency_key_or_throw",
        "sync-materialize:v1:",
        "sync-chunk-receipt:v1:",
    ],
    "docs/0073-rev0683-materialize-resume-executor.md": [
        "Rev0683 — materialize resume executor",
        "execute_sync_session_checkpoint_resume_materializations",
        "MaterializeStagedFile",
        "CleanupCommittedStaging",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0683 product slice — MaterializeStagedFile resume executor",
        "execute_sync_session_checkpoint_resume_materializations",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0683",
        "Rev0683 priority note",
        "CleanupCommittedStaging",
        "local overwrite preflight evidence",
    ],
    "bin/HISTORY.md": [
        "rev0683",
        "MaterializeStagedFile resume executor",
        "rev0682 runnable binary is intentionally omitted",
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
        raise AssertionError("missing required rev0683 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0683 package must not carry the rev0682 active binary")
    mode = (ROOT / ACTIVE_BINARY).stat().st_mode
    if mode & 0o111 == 0:
        raise AssertionError("active rev0683 binary must be executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0683-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0683-materialize-resume-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0683-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0683-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    asan_build = (ROOT / "audit/logs/rev0683-narrow-asan-ubsan-sync-domain-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in asan_build:
        raise AssertionError("narrow sanitizer build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0683" or audit.get("parent_revision") != "rev0682":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "materialize-resume-executor":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0683 must claim C++ behavior changed")
    checks = audit.get("materialize_resume_checks", [])
    if not any("sync-chunk-receipt:v1" in item for item in checks):
        raise AssertionError("audit materialization checks must mention receipt idempotency keys")
    if not any("sync-materialize:v1" in item for item in checks):
        raise AssertionError("audit materialization checks must mention materialization idempotency keys")
    if not any("CleanupCommittedStaging" in item for item in checks):
        raise AssertionError("audit materialization checks must mention cleanup transition")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0683-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0683" or manifest.get("parent_revision") != "rev0682":
        raise AssertionError("rev0683 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-materialize-resume-executor":
        raise AssertionError("rev0683 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0683 product mission tag mismatch")
    if manifest.get("codename") != "materialize-resume-executor":
        raise AssertionError("rev0683 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0683")
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
        expected_files.append({"path": rel, "sha256": sha_file(path), "size_bytes": path.stat().st_size})
    expected_files.sort(key=lambda item: item["path"])
    actual_files = sorted(manifest.get("files", []), key=lambda item: item.get("path", ""))
    if actual_files != expected_files:
        raise AssertionError("manifest file listing/hash set mismatch")


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
