#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0686 resume transfer executor package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=236 failed=0"
ACTIVE_BINARY = "bin/rev0686/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0685/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0686-resume-transfer-executor-audit.json"
MANIFEST = ROOT / "schema/rev0686/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0686-resume-transfer-executor-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0686/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0076-rev0686-resume-transfer-executor.md",
    "audit/rev0686-resume-transfer-executor-audit.json",
    "audit/rev0686-resume-transfer-executor-source.patch",
    "audit/logs/rev0686-release-configure.log",
    "audit/logs/rev0686-release-build.log",
    "audit/logs/rev0686-release-ctest.log",
    "audit/logs/rev0686-resume-transfer-executor-selftest.log",
    "audit/logs/rev0686-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0686-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0686-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0686-binary-sha256.txt",
    "audit/logs/rev0686-binary-ldd.txt",
    "tools/validate_rev0686_resume_transfer_executor.py",
    "schema/rev0686/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0686",
        "ResumeTransfer fake-peer executor",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        EXPECTED_SELFTEST,
        "sync-resume-transfer-execute:v1:",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0686",
        "SyncSessionCheckpointResumeTransferExecutionResult",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        EXPECTED_SELFTEST,
        "sync-resume-transfer-execute:v1:",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncSessionCheckpointResumeTransferExecutionOptions",
        "struct SyncSessionCheckpointResumeTransferFileExecutionResult",
        "struct SyncSessionCheckpointResumeTransferExecutionResult",
        "SyncValidationResult execute_sync_session_checkpoint_resume_transfer_workorders",
        "std::uint64_t receipt_rows_upserted = 0;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "sync session checkpoint resume transfer executor fetches planned fake-peer chunks into staged receipt evidence",
        "sync session checkpoint resume transfer executor promotes completed staged work to materialization restart state",
        "sync-resume-transfer-execute:v1:",
        "sync-chunk-receipt:v1:",
    ],
    "docs/0076-rev0686-resume-transfer-executor.md": [
        "Rev0686 — resume transfer fake-peer executor",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "plan_sync_session_checkpoint_resume_transfers",
        "sync-resume-transfer-execute:v1:",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0686 product slice — ResumeTransfer fake-peer executor",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0686",
        "Rev0686 priority note",
        "Persist resume transfer work orders",
        "worker claim/reclaim policy",
    ],
    "bin/HISTORY.md": [
        "rev0686",
        "ResumeTransfer fake-peer executor",
        "rev0685 runnable binary is intentionally omitted",
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
        raise AssertionError("missing required rev0686 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0686 package must not carry the rev0685 active binary")
    mode = (ROOT / ACTIVE_BINARY).stat().st_mode
    if mode & 0o111 == 0:
        raise AssertionError("active rev0686 binary must be executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0686-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0686-resume-transfer-executor-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0686-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0686-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    asan_build = (ROOT / "audit/logs/rev0686-narrow-asan-ubsan-sync-domain-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in asan_build:
        raise AssertionError("narrow sanitizer build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0686" or audit.get("parent_revision") != "rev0685":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "resume-transfer-executor":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-resume-transfer-executor":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0686 must claim C++ behavior changed")
    checks = audit.get("transfer_executor_checks", [])
    required_mentions = [
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "plan_sync_session_checkpoint_resume_transfers",
        "sync_session_apply_intents",
        "sync_session_chunk_receipts",
        "sync-resume-transfer-execute:v1",
        "sync-chunk-receipt:v1",
        "source manifest chunk rows",
        "MaterializeStagedFile",
    ]
    for mention in required_mentions:
        if not any(mention in item for item in checks):
            raise AssertionError(f"audit transfer executor checks must mention {mention}")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0686-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0686" or manifest.get("parent_revision") != "rev0685":
        raise AssertionError("rev0686 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-resume-transfer-executor":
        raise AssertionError("rev0686 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0686 product mission tag mismatch")
    if manifest.get("codename") != "resume-transfer-executor":
        raise AssertionError("rev0686 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0686")
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
