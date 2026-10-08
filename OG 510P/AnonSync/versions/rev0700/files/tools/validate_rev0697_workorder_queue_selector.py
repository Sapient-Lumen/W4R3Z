#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0697 workorder queue selector package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=271 failed=0"
ACTIVE_BINARY = "bin/rev0697/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0696/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0697-workorder-queue-selector-audit.json"
MANIFEST = ROOT / "schema/rev0697/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0697-workorder-queue-selector-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0697/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0087-rev0697-workorder-queue-selector.md",
    "docs/0086-rev0696-terminal-reset.md",
    "docs/0085-rev0695-workorder-quarantine.md",
    "docs/0084-rev0694-retry-at-backoff.md",
    "docs/0083-rev0693-attempt-cap-abandon.md",
    "docs/0082-rev0692-reclaim-event-history.md",
    "docs/0081-rev0691-resume-lease-reclaim.md",
    "docs/0080-rev0690-resume-claim-split.md",
    "docs/0079-rev0689-mission-reclaim-compass.md",
    "docs/0078-rev0688-resume-workorder-lease.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0697-workorder-queue-selector-audit.json",
    "audit/rev0697-workorder-queue-selector-source.patch",
    "audit/logs/rev0697-release-configure.log",
    "audit/logs/rev0697-release-build-final.log",
    "audit/logs/rev0697-release-ctest.log",
    "audit/logs/rev0697-packaged-sync-domain-selftest.log",
    "audit/logs/rev0697-asan-ubsan-configure.log",
    "audit/logs/rev0697-asan-ubsan-build-final.log",
    "audit/logs/rev0697-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0697-binary-sha256.txt",
    "audit/logs/rev0697-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0697_workorder_queue_selector.py",
    "schema/rev0697/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0697",
        "Rev0697 is **code-bearing**",
        "select_sync_session_checkpoint_resume_transfer_workorder_queue",
        "folder convergence under evidence-bound local truth",
        "bounded persisted daemon scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "bin/HISTORY.md": [
        "rev0697",
        ACTIVE_BINARY,
        "read-only persisted resume-transfer workorder queue selector",
        "rev0696 runnable binary is intentionally omitted",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0697",
        "SyncSessionCheckpointResumeTransferWorkorderQueueOptions",
        "select_sync_session_checkpoint_resume_transfer_workorder_queue",
        "bounded scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "docs/0087-rev0697-workorder-queue-selector.md": [
        "Rev0697 — workorder queue selector",
        "OwnedClaimReady",
        "ExpiredCoolingDown",
        "ExpiredReclaimReady",
        "ExpiredAbandonReady",
        "CompletedIgnored",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "current rev0697 code slice",
        "bounded scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0697",
        "bounded persisted daemon scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "SyncSessionCheckpointResumeTransferWorkorderQueueKind",
        "SyncSessionCheckpointResumeTransferWorkorderQueueOptions",
        "SyncSessionCheckpointResumeTransferWorkorderQueueFact",
        "SyncSessionCheckpointResumeTransferWorkorderQueueResult",
        "select_sync_session_checkpoint_resume_transfer_workorder_queue",
        "ExpiredAbandonReady",
        "CompletedIgnored",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "select_sync_session_checkpoint_resume_transfer_workorder_queue",
        "out.read_only_scan_completed = true",
        "ExpiredCoolingDown",
        "ExpiredReclaimReady",
        "ExpiredAbandonReady",
        "CompletedIgnored",
        "queue selector exposes owned live claimed rows",
        "queue selector ignores completed rows by default",
    ],
    "audit/rev0697-workorder-queue-selector-audit.json": [
        "workorder-queue-selector",
        "OwnedClaimReady",
        "ExpiredAbandonReady",
        "bounded persisted daemon scheduler pass",
    ],
    "audit/rev0697-workorder-queue-selector-source.patch": [
        "0087-rev0697-workorder-queue-selector.md",
        "select_sync_session_checkpoint_resume_transfer_workorder_queue",
        "validate_rev0697_workorder_queue_selector.py",
    ],
}

QUEUE_KIND_TOKENS = [
    "OwnedClaimReady",
    "LiveClaimedByOther",
    "ExpiredCoolingDown",
    "ExpiredReclaimReady",
    "ExpiredAbandonReady",
    "AbandonedReview",
    "QuarantinedReview",
    "CompletedIgnored",
]


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "__pycache__" in rel or rel.endswith(".pyc"):
            continue
        yield rel


def assert_exists() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0697 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0696 active binary must be omitted from the slim rev0697 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0697 binary must be executable")

    header = (ROOT / "cpp/anonsync_core/include/anonsync_core.hpp").read_text(errors="replace")
    source = (ROOT / "cpp/anonsync_core/src/sync_domain.cpp").read_text(errors="replace")
    for token in QUEUE_KIND_TOKENS:
        if token not in header or token not in source:
            raise AssertionError(f"queue kind missing from public header or source: {token}")
    if "queue_result" not in source or "sqlite3_open_v2" not in source:
        raise AssertionError("queue selector must be a concrete sqlite-backed read model")
    if "UPDATE sync_session_resume_transfer_workorders" in source.split("select_sync_session_checkpoint_resume_transfer_workorder_queue", 1)[1].split("execute_sync_session_checkpoint_resume_cycle", 1)[0]:
        raise AssertionError("queue selector slice must not update transfer workorders")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    if EXPECTED_CTEST not in (ROOT / "audit/logs/rev0697-release-ctest.log").read_text(errors="replace"):
        raise AssertionError("release ctest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0697-packaged-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0697-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0697-release-build-final.log").read_text(errors="replace"):
        raise AssertionError("release build final log missing built target line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0697-asan-ubsan-build-final.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0697 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0697" or audit.get("parent_revision") != "rev0696":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "workorder-queue-selector":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-workorder-queue-selector":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0697 must be marked code-bearing")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    for token in QUEUE_KIND_TOKENS:
        if token not in audit.get("queue_kinds", []):
            raise AssertionError(f"audit queue kind missing: {token}")
    validation = audit.get("validation", {})
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit release ctest summary mismatch")
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if validation.get("asan_ubsan_sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit asan/ubsan summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")
    if audit.get("next_p0") != "bounded persisted daemon scheduler pass":
        raise AssertionError("audit next P0 mismatch")


def assert_binary_hash() -> None:
    actual = sha_file(ROOT / ACTIVE_BINARY)
    text = (ROOT / "audit/logs/rev0697-binary-sha256.txt").read_text(errors="replace")
    if actual not in text or ACTIVE_BINARY not in text:
        raise AssertionError("binary sha256 log mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0697":
        raise AssertionError("manifest revision_id mismatch")
    if manifest.get("parent_revision") != "rev0696":
        raise AssertionError("manifest parent_revision mismatch")
    if manifest.get("codename") != "workorder-queue-selector":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("manifest active binary hash mismatch")
    expected_files = sorted(rel for rel in rel_files() if rel not in EXCLUDED_MUTABLE)
    recorded = manifest.get("files", [])
    recorded_names = sorted(entry.get("path") for entry in recorded)
    if recorded_names != expected_files:
        missing = sorted(set(expected_files) - set(recorded_names))
        extra = sorted(set(recorded_names) - set(expected_files))
        raise AssertionError(f"manifest file set mismatch; missing={missing[:10]} extra={extra[:10]}")
    for entry in recorded:
        rel = entry.get("path")
        if entry.get("sha256") != sha_file(ROOT / rel):
            raise AssertionError("manifest sha mismatch for " + rel)
    if sorted(manifest.get("excluded_mutable_files", [])) != sorted(EXCLUDED_MUTABLE):
        raise AssertionError("manifest excluded mutable files mismatch")


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
