#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0700 scheduler executor boundary package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=285 failed=0"
ACTIVE_BINARY = "bin/rev0700/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0699/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0700-scheduler-executor-boundary-audit.json"
MANIFEST = ROOT / "schema/rev0700/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0700-scheduler-executor-boundary-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0700/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0090-rev0700-scheduler-executor-boundary.md",
    "docs/0089-rev0699-scheduler-batch-boundary.md",
    "docs/0088-rev0698-scheduler-action-plan.md",
    "docs/0087-rev0697-workorder-queue-selector.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0700-scheduler-executor-boundary-audit.json",
    "audit/rev0700-scheduler-executor-boundary-source.patch",
    "audit/logs/rev0700-release-configure.log",
    "audit/logs/rev0700-release-build-final.log",
    "audit/logs/rev0700-release-build-all.log",
    "audit/logs/rev0700-release-ctest.log",
    "audit/logs/rev0700-packaged-sync-domain-selftest.log",
    "audit/logs/rev0700-asan-ubsan-configure.log",
    "audit/logs/rev0700-asan-ubsan-build-final.log",
    "audit/logs/rev0700-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0700-binary-sha256.txt",
    "audit/logs/rev0700-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0700_scheduler_executor_boundary.py",
    "schema/rev0700/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0700",
        "Rev0700 is **code-bearing**",
        "allowed_execution_idempotency_keys",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "folder convergence under evidence-bound local truth",
        "persisted daemon loop",
        EXPECTED_SELFTEST,
    ],
    "bin/HISTORY.md": [
        "rev0700",
        ACTIVE_BINARY,
        "bounded mutating scheduler executor",
        "rev0699 runnable binary is intentionally omitted",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0700",
        "allowed_execution_idempotency_keys",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "bounded scheduler executor",
        EXPECTED_SELFTEST,
    ],
    "docs/0090-rev0700-scheduler-executor-boundary.md": [
        "Rev0700 — scheduler executor boundary",
        "allowed_execution_idempotency_keys",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "current rev0700 code slice",
        "bounded mutating scheduler execution",
        "persisted bounded daemon worker loop",
        EXPECTED_SELFTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0700",
        "bounded scheduler executor",
        "scheduler executor as a bridge",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "allowed_execution_idempotency_keys",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "mutating_action_groups_selected",
        "execution_key_filters_built",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "resume_transfer_execution_key_filter_allows",
        "unique_resume_transfer_execution_keys_or_throw",
        "allowed_execution_idempotency_keys",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "claim_or_abandon_filter_keys",
        "execute_filter_keys",
        "sync session checkpoint resume transfer scheduler executor refuses to mutate a deferred partial execution group",
        "sync session checkpoint resume transfer scheduler executor reclaims only the returned expired complete group",
        "sync session checkpoint resume transfer scheduler executor abandons only the returned expired attempt-cap group",
        "sync session checkpoint resume transfer scheduler executor executes only the returned owned complete group",
    ],
    "audit/rev0700-scheduler-executor-boundary-audit.json": [
        "scheduler-executor-boundary",
        "bounded mutating persisted scheduler executor",
        "allowed_execution_idempotency_keys",
        EXPECTED_SELFTEST,
    ],
    "audit/rev0700-scheduler-executor-boundary-source.patch": [
        "0090-rev0700-scheduler-executor-boundary.md",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions",
        "allowed_execution_idempotency_keys",
        "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "validate_rev0700_scheduler_executor_boundary.py",
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
        raise AssertionError("missing required rev0700 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0699 active binary must be omitted from the slim rev0700 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0700 binary must be executable")

    header = (ROOT / "cpp/anonsync_core/include/anonsync_core.hpp").read_text(errors="replace")
    source = (ROOT / "cpp/anonsync_core/src/sync_domain.cpp").read_text(errors="replace")
    for token in ACTION_KIND_TOKENS:
        if token not in header or token not in source:
            raise AssertionError(f"scheduler action kind missing from public header or source: {token}")

    for signature in [
        "SyncSessionCheckpointResumeTransferClaimOptions",
        "SyncSessionCheckpointResumeTransferExecutionOptions",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult",
    ]:
        if signature not in header:
            raise AssertionError("missing public scheduler executor surface in header: " + signature)

    executor_slice = source.split("execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass", 1)[1].split("execute_sync_session_checkpoint_resume_cycle", 1)[0]
    forbidden = [
        "UPDATE sync_session_resume_transfer_workorders",
        "INSERT INTO sync_session_resume_transfer_workorders",
        "sqlite_exec_or_throw(handle.db, \"BEGIN",
        "sqlite_prepare_or_throw(handle.db",
    ]
    for token in forbidden:
        if token in executor_slice:
            raise AssertionError("scheduler executor must delegate mutation and not perform direct SQLite workorder writes: " + token)
    for token in [
        "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass",
        "claim_sync_session_checkpoint_resume_transfer_workorders",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "allowed_execution_idempotency_keys = claim_or_abandon_keys",
        "allowed_execution_idempotency_keys = execute_keys",
        "claim/abandon mutator did not consume exactly the selected scheduler actions",
        "owned-claim mutator did not consume exactly the selected scheduler actions",
    ]:
        if token not in executor_slice:
            raise AssertionError("scheduler executor is missing required delegation/filter token: " + token)


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    if EXPECTED_CTEST not in (ROOT / "audit/logs/rev0700-release-ctest.log").read_text(errors="replace"):
        raise AssertionError("release ctest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0700-packaged-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0700-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0700-release-build-final.log").read_text(errors="replace"):
        raise AssertionError("release build final log missing built target line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0700-asan-ubsan-build-final.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0700 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0700" or audit.get("parent_revision") != "rev0699":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "scheduler-executor-boundary":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-scheduler-executor-boundary":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0700 must be marked code-bearing")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    validation = audit.get("validation", {})
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit release ctest summary mismatch")
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("asan_ubsan_sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit asan/ubsan selftest summary mismatch")
    for field in [
        "SyncSessionCheckpointResumeTransferClaimOptions.allowed_execution_idempotency_keys",
        "SyncSessionCheckpointResumeTransferExecutionOptions.allowed_execution_idempotency_keys",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult.execution_key_filters_built",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult.workorder_rows_completed",
    ]:
        if field not in audit.get("new_public_fields", []):
            raise AssertionError("audit missing new public field: " + field)
    if "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass" not in audit.get("new_public_functions", []):
        raise AssertionError("audit missing scheduler executor function")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("codename") != "scheduler-executor-boundary":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("manifest active binary sha mismatch")
    if set(manifest.get("excluded_mutable_files", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest excluded mutable files mismatch")
    manifest_files = {item["path"]: item for item in manifest.get("files", [])}
    actual_files = set(rel_files()) - EXCLUDED_MUTABLE
    if set(manifest_files) != actual_files:
        missing = sorted(actual_files - set(manifest_files))[:20]
        extra = sorted(set(manifest_files) - actual_files)[:20]
        raise AssertionError(f"manifest file set mismatch missing={missing} extra={extra}")
    for rel, item in manifest_files.items():
        path = ROOT / rel
        if item.get("sha256") != sha_file(path):
            raise AssertionError("manifest sha mismatch for " + rel)
        if item.get("size_bytes") != path.stat().st_size:
            raise AssertionError("manifest size mismatch for " + rel)


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
