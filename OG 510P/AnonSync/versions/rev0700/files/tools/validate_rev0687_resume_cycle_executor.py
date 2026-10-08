#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0687 resume cycle executor package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=237 failed=0"
ACTIVE_BINARY = "bin/rev0687/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0686/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0687-resume-cycle-executor-audit.json"
MANIFEST = ROOT / "schema/rev0687/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0687-resume-cycle-executor-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0687/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0077-rev0687-resume-cycle-executor.md",
    "audit/rev0687-resume-cycle-executor-audit.json",
    "audit/rev0687-resume-cycle-executor-source.patch",
    "audit/logs/rev0687-release-configure.log",
    "audit/logs/rev0687-release-build.log",
    "audit/logs/rev0687-release-ctest.log",
    "audit/logs/rev0687-resume-cycle-executor-selftest.log",
    "audit/logs/rev0687-binary-sha256.txt",
    "audit/logs/rev0687-binary-ldd.txt",
    "tools/validate_rev0687_resume_cycle_executor.py",
    "schema/rev0687/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0687",
        "resume cycle drain executor",
        "execute_sync_session_checkpoint_resume_cycle",
        EXPECTED_SELFTEST,
        "No sanitizer pass is claimed for rev0687",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0687",
        "SyncSessionCheckpointResumeCycleResult",
        "execute_sync_session_checkpoint_resume_cycle",
        EXPECTED_SELFTEST,
        "bounded restart-cycle executor",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncSessionCheckpointResumeCycleOptions",
        "struct SyncSessionCheckpointResumeCycleResult",
        "SyncValidationResult execute_sync_session_checkpoint_resume_cycle",
        "bool require_final_staging_artifacts_cleaned = true;",
        "SyncSessionCheckpointResumeTransferExecutionResult transfer_execution;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "execute_sync_session_checkpoint_resume_cycle",
        "sync session checkpoint resume cycle executor drains transfer, materialization, and cleanup branches to strict convergence",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "execute_sync_session_checkpoint_resume_materializations",
        "execute_sync_session_checkpoint_resume_cleanups",
    ],
    "docs/0077-rev0687-resume-cycle-executor.md": [
        "Rev0687 — resume cycle drain executor",
        "execute_sync_session_checkpoint_resume_cycle",
        "action plan → fake-peer transfer executor",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0687 product slice — bounded resume-cycle drain executor",
        "execute_sync_session_checkpoint_resume_cycle",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0687",
        "Persist resume transfer work orders",
        EXPECTED_SELFTEST,
        "Sanitizer evidence should be restored",
    ],
    "bin/HISTORY.md": [
        "rev0687",
        ACTIVE_BINARY,
        "bounded resume-cycle drain executor",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files():
    for path in ROOT.rglob("*"):
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            if "__pycache__" in rel or rel.endswith(".pyc"):
                continue
            yield rel


def assert_required_files() -> None:
    missing = [rel for rel in REQUIRED_CURRENT_FILES if not (ROOT / rel).exists()]
    if missing:
        raise AssertionError("missing rev0687 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0687 package must not carry the rev0686 active binary")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0687 binary must be executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0687-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0687-resume-cycle-executor-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    build = (ROOT / "audit/logs/rev0687-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0687" or audit.get("parent_revision") != "rev0686":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "resume-cycle-executor":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-resume-cycle-executor":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0687 must claim C++ behavior changed")
    checks = audit.get("resume_cycle_checks", [])
    required_mentions = [
        "execute_sync_session_checkpoint_resume_cycle",
        "plan_sync_session_checkpoint_resume_actions",
        "execute_sync_session_checkpoint_resume_transfer_workorders",
        "execute_sync_session_checkpoint_resume_materializations",
        "execute_sync_session_checkpoint_resume_cleanups",
        "AlreadyConverged",
    ]
    for mention in required_mentions:
        if not any(mention in item for item in checks):
            raise AssertionError(f"audit resume cycle checks must mention {mention}")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0687-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0687" or manifest.get("parent_revision") != "rev0686":
        raise AssertionError("rev0687 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-resume-cycle-executor":
        raise AssertionError("rev0687 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0687 product mission tag mismatch")
    if manifest.get("codename") != "resume-cycle-executor":
        raise AssertionError("rev0687 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    if set(manifest.get("excluded_mutable_evidence", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest mutable exclusions mismatch")
    validation = manifest.get("validation", {})
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("manifest selftest mismatch")
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("manifest ctest mismatch")
    files = {item["path"]: item for item in manifest.get("files", [])}
    for rel in REQUIRED_CURRENT_FILES:
        if rel not in files and rel not in EXCLUDED_MUTABLE:
            raise AssertionError(f"manifest missing required file: {rel}")
    for rel in rel_files():
        if rel in EXCLUDED_MUTABLE:
            continue
        item = files.get(rel)
        if item is None:
            raise AssertionError(f"manifest missing packaged file: {rel}")
        path = ROOT / rel
        if item.get("size_bytes") != path.stat().st_size:
            raise AssertionError(f"manifest size mismatch: {rel}")
        if item.get("sha256") != sha_file(path):
            raise AssertionError(f"manifest sha mismatch: {rel}")


def main() -> None:
    assert_required_files()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_binary_hash()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
