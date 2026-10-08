#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0698 scheduler action plan package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=276 failed=0"
ACTIVE_BINARY = "bin/rev0698/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0697/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0698-scheduler-action-plan-audit.json"
MANIFEST = ROOT / "schema/rev0698/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0698-scheduler-action-plan-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0698/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0088-rev0698-scheduler-action-plan.md",
    "docs/0087-rev0697-workorder-queue-selector.md",
    "docs/0086-rev0696-terminal-reset.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0698-scheduler-action-plan-audit.json",
    "audit/rev0698-scheduler-action-plan-source.patch",
    "audit/logs/rev0698-release-configure.log",
    "audit/logs/rev0698-release-build-final.log",
    "audit/logs/rev0698-release-ctest.log",
    "audit/logs/rev0698-packaged-sync-domain-selftest.log",
    "audit/logs/rev0698-asan-ubsan-configure.log",
    "audit/logs/rev0698-asan-ubsan-build-final.log",
    "audit/logs/rev0698-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0698-binary-sha256.txt",
    "audit/logs/rev0698-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0698_scheduler_action_plan.py",
    "schema/rev0698/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0698",
        "Rev0698 is **code-bearing**",
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "folder convergence under evidence-bound local truth",
        "first mutating persisted scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "bin/HISTORY.md": [
        "rev0698",
        ACTIVE_BINARY,
        "bounded scheduler action planner",
        "rev0697 runnable binary is intentionally omitted",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0698",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions",
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "first mutating persisted daemon worker loop",
        EXPECTED_SELFTEST,
    ],
    "docs/0088-rev0698-scheduler-action-plan.md": [
        "Rev0698 — scheduler action plan",
        "ExecuteOwnedClaim",
        "ClaimOrReclaimExpired",
        "AbandonExpired",
        "WaitRetryBackoff",
        "ReviewQuarantined",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "current rev0698 code slice",
        "scheduler action planning",
        EXPECTED_SELFTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0698",
        "first mutating persisted scheduler pass",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult",
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "ExecuteOwnedClaim",
        "IgnoreCompleted",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result)",
        "ExecuteOwnedClaim",
        "ClaimOrReclaimExpired",
        "AbandonExpired",
        "WaitRetryBackoff",
        "scheduler pass maps owned queue facts to bounded execute-owned actions",
        "scheduler pass waits instead of reclaiming during retry-at cooldown",
        "scheduler pass maps retry-open attempt-cap rows to abandon actions",
    ],
    "audit/rev0698-scheduler-action-plan-audit.json": [
        "scheduler-action-plan",
        "ExecuteOwnedClaim",
        "ClaimOrReclaimExpired",
        "first mutating persisted scheduler pass",
    ],
    "audit/rev0698-scheduler-action-plan-source.patch": [
        "0088-rev0698-scheduler-action-plan.md",
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "validate_rev0698_scheduler_action_plan.py",
    ],
}

ACTION_KIND_TOKENS = [
    "ExecuteOwnedClaim",
    "ClaimOrReclaimExpired",
    "AbandonExpired",
    "ObserveLiveClaimedByOther",
    "WaitRetryBackoff",
    "ReviewAbandoned",
    "ReviewQuarantined",
    "IgnoreCompleted",
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
        raise AssertionError("missing required rev0698 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0697 active binary must be omitted from the slim rev0698 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0698 binary must be executable")

    header = (ROOT / "cpp/anonsync_core/include/anonsync_core.hpp").read_text(errors="replace")
    source = (ROOT / "cpp/anonsync_core/src/sync_domain.cpp").read_text(errors="replace")
    for token in ACTION_KIND_TOKENS:
        if token not in header or token not in source:
            raise AssertionError(f"scheduler action kind missing from public header or source: {token}")
    if "SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result" not in source:
        raise AssertionError("scheduler action planner must consume the queue selector result")
    scheduler_slice = source.split("plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass", 1)[1].split("execute_sync_session_checkpoint_resume_cycle", 1)[0]
    forbidden = ["UPDATE sync_session_resume_transfer_workorders", "INSERT INTO sync_session_resume_transfer_workorders", "sqlite_exec_or_throw(handle.db, \"BEGIN"]
    for token in forbidden:
        if token in scheduler_slice:
            raise AssertionError("scheduler action planner must not mutate transfer workorders: " + token)


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    if EXPECTED_CTEST not in (ROOT / "audit/logs/rev0698-release-ctest.log").read_text(errors="replace"):
        raise AssertionError("release ctest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0698-packaged-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0698-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0698-release-build-final.log").read_text(errors="replace"):
        raise AssertionError("release build final log missing built target line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0698-asan-ubsan-build-final.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0698 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0698" or audit.get("parent_revision") != "rev0697":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "scheduler-action-plan":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-scheduler-action-plan":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0698 must be marked code-bearing")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    for token in ACTION_KIND_TOKENS:
        if token not in audit.get("scheduler_action_kinds", []):
            raise AssertionError(f"audit scheduler action kind missing: {token}")
    validation = audit.get("validation", {})
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit release ctest summary mismatch")
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if validation.get("asan_ubsan_sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit asan/ubsan summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")
    if audit.get("next_p0") != "first mutating persisted scheduler pass":
        raise AssertionError("audit next P0 mismatch")


def assert_binary_hash() -> None:
    actual = sha_file(ROOT / ACTIVE_BINARY)
    text = (ROOT / "audit/logs/rev0698-binary-sha256.txt").read_text(errors="replace")
    if actual not in text or ACTIVE_BINARY not in text:
        raise AssertionError("binary sha256 log mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0698":
        raise AssertionError("manifest revision_id mismatch")
    if manifest.get("parent_revision") != "rev0697":
        raise AssertionError("manifest parent_revision mismatch")
    if manifest.get("codename") != "scheduler-action-plan":
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
