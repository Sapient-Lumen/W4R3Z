#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0685 resume transfer planner package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=234 failed=0"
ACTIVE_BINARY = "bin/rev0685/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0684/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0685-resume-transfer-planner-audit.json"
MANIFEST = ROOT / "schema/rev0685/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0685-resume-transfer-planner-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0685/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0075-rev0685-resume-transfer-planner.md",
    "audit/rev0685-resume-transfer-planner-audit.json",
    "audit/rev0685-resume-transfer-planner-source.patch",
    "audit/logs/rev0685-release-configure.log",
    "audit/logs/rev0685-release-build.log",
    "audit/logs/rev0685-release-ctest.log",
    "audit/logs/rev0685-resume-transfer-planner-selftest.log",
    "audit/logs/rev0685-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0685-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0685-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0685-binary-sha256.txt",
    "audit/logs/rev0685-binary-ldd.txt",
    "tools/validate_rev0685_resume_transfer_planner.py",
    "schema/rev0685/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0685",
        "ResumeTransfer work-order planner",
        "plan_sync_session_checkpoint_resume_transfers",
        EXPECTED_SELFTEST,
        "sync-resume-transfer-request:v1:",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0685",
        "SyncSessionCheckpointResumeTransferPlanResult",
        "plan_sync_session_checkpoint_resume_transfers",
        EXPECTED_SELFTEST,
        "sync-resume-peer-schedule:v1:",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncSessionCheckpointResumeTransferPlanOptions",
        "struct SyncSessionCheckpointResumeTransferFilePlan",
        "struct SyncSessionCheckpointResumeTransferPlanResult",
        "SyncValidationResult plan_sync_session_checkpoint_resume_transfers",
        "std::uint64_t peer_assigned_chunks = 0;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "plan_sync_session_checkpoint_resume_transfers",
        "sync session checkpoint resume transfer planner turns ResumeTransfer evidence into peer-bound missing-chunk work",
        "sync-resume-transfer-request:v1:",
        "sync-resume-peer-request:v1:",
        "sync-resume-peer-schedule:v1:",
    ],
    "docs/0075-rev0685-resume-transfer-planner.md": [
        "Rev0685 — resume transfer work-order planner",
        "plan_sync_session_checkpoint_resume_transfers",
        "ResumeTransfer",
        "sync-resume-transfer-request:v1:",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0685 product slice — ResumeTransfer work-order planner",
        "plan_sync_session_checkpoint_resume_transfers",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0685",
        "Rev0685 priority note",
        "Persist resume transfer work orders",
        "Add a `ResumeTransfer` executor",
    ],
    "bin/HISTORY.md": [
        "rev0685",
        "ResumeTransfer work-order planner",
        "rev0684 runnable binary is intentionally omitted",
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
        raise AssertionError("missing required rev0685 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0685 package must not carry the rev0684 active binary")
    mode = (ROOT / ACTIVE_BINARY).stat().st_mode
    if mode & 0o111 == 0:
        raise AssertionError("active rev0685 binary must be executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0685-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0685-resume-transfer-planner-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0685-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0685-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    asan_build = (ROOT / "audit/logs/rev0685-narrow-asan-ubsan-sync-domain-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in asan_build:
        raise AssertionError("narrow sanitizer build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0685" or audit.get("parent_revision") != "rev0684":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "resume-transfer-planner":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-resume-transfer-planner":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0685 must claim C++ behavior changed")
    checks = audit.get("transfer_planner_checks", [])
    required_mentions = [
        "plan_sync_session_checkpoint_resume_transfers",
        "ResumeTransfer",
        "RetryTransfer",
        "sync-resume-transfer-request:v1",
        "sync-resume-peer-request:v1",
        "sync-resume-peer-schedule:v1",
        "read-only",
        "max_chunks_per_request",
        "max_chunks_per_peer_round",
    ]
    for mention in required_mentions:
        if not any(mention in item for item in checks):
            raise AssertionError(f"audit transfer planner checks must mention {mention}")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0685-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0685" or manifest.get("parent_revision") != "rev0684":
        raise AssertionError("rev0685 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-resume-transfer-planner":
        raise AssertionError("rev0685 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0685 product mission tag mismatch")
    if manifest.get("codename") != "resume-transfer-planner":
        raise AssertionError("rev0685 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0685")
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
